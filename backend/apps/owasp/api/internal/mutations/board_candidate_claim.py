"""OWASP Board Candidate Claim GraphQL mutations."""

import json
import logging

import strawberry
from django.db import transaction
from django.db.models.base import ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone
from strawberry.types import Info

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_of_directors import BoardOfDirectors

logger = logging.getLogger(__name__)


@strawberry.input
class CreateClaimInput:
    """Input for creating a claim."""

    description: str
    title: str
    year: int


@strawberry.input
class UpdateClaimInput:
    """Input for updating a claim."""

    claim_id: strawberry.relay.GlobalID
    description: str | None = None
    title: str | None = None


@strawberry.input
class DiscardClaimInput:
    """Input for discarding a claim."""

    claim_id: strawberry.relay.GlobalID


@strawberry.input
class SubmitClaimInput:
    """Input for submitting a claim."""

    claim_id: strawberry.relay.GlobalID


@strawberry.input
class WithdrawClaimInput:
    """Input for withdrawing a claim."""

    claim_id: strawberry.relay.GlobalID
    withdrawn_reason: str


# TODO(rudransh-shrivastava): add reordering mutation.


@strawberry.type
class ClaimResult:
    """Result for claim mutations."""

    ok: bool
    code: str | None = None
    message: str | None = None


@strawberry.type
class BoardCandidateClaimMutations:
    """Board Candidate Claim mutations."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def create_board_candidate_claim(
        self, info: Info, input_data: CreateClaimInput
    ) -> ClaimResult:
        """Create a new draft claim for a candidate."""
        try:
            board = BoardOfDirectors.objects.get(year=input_data.year)
        except BoardOfDirectors.DoesNotExist:
            return ClaimResult(
                ok=False,
                code="NOT_FOUND",
                message=f"No board election found for the year {input_data.year}.",
            )

        candidate = board.get_candidate(login=info.context.request.user)
        if not candidate:
            return ClaimResult(
                ok=False,
                code="FORBIDDEN",
                message="You are not registered as an active candidate for this election.",
            )

        try:
            BoardCandidateClaim.objects.create(
                board=board,
                candidate=candidate,
                description=input_data.description,
                title=input_data.title,
            )
        except IntegrityError:
            logger.warning(
                "Error creating Board Candidate Claim for candidate %s, year %s",
                candidate.login,
                input_data.year,
            )
            return ClaimResult(
                ok=False,
                code="ERROR",
                message="Something went wrong.",
            )
        except ValidationError as e:
            return ClaimResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=json.dumps(e.message_dict),
            )

        return ClaimResult(ok=True, code="SUCCESS", message="Claim created successfully.")

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def update_board_candidate_claim(
        self, info: Info, input_data: UpdateClaimInput
    ) -> ClaimResult:
        """Update a draft claim."""
        user = info.context.request.user

        try:
            claim = BoardCandidateClaim.objects.select_for_update().get(
                pk=int(input_data.claim_id.node_id)
            )
        except BoardCandidateClaim.DoesNotExist:
            return ClaimResult(ok=False, code="NOT_FOUND", message="Claim not found.")

        if claim.candidate.member.login != str(user):
            return ClaimResult(ok=False, code="FORBIDDEN", message="Access denied.")

        if claim.is_locked:
            return ClaimResult(ok=False, code="LOCKED", message="Cannot update a locked claim.")

        update_fields = []
        if input_data.title:
            claim.title = input_data.title
            update_fields.append("title")
        if input_data.description:
            claim.description = input_data.description
            update_fields.append("description")

        try:
            claim.save(update_fields=update_fields)
        except IntegrityError:
            logger.warning(
                "Error updating Board Candidate Claim for candidate %s, title %s",
                claim.candidate.member.login,
                input_data.title,
            )
            return ClaimResult(
                ok=False,
                code="ERROR",
                message="Something went wrong.",
            )
        except ValidationError as e:
            return ClaimResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=json.dumps(e.message_dict),
            )

        return ClaimResult(ok=True, code="SUCCESS", message="Claim updated successfully.")

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def discard_board_candidate_claim(
        self, info: Info, input_data: DiscardClaimInput
    ) -> ClaimResult:
        """Discard a claim."""
        user = info.context.request.user

        try:
            claim = BoardCandidateClaim.objects.select_for_update().get(
                pk=int(input_data.claim_id.node_id)
            )
        except BoardCandidateClaim.DoesNotExist:
            return ClaimResult(ok=False, code="NOT_FOUND", message="Claim not found.")

        if claim.candidate.member.login != str(user):
            return ClaimResult(ok=False, code="FORBIDDEN", message="Access denied.")

        if claim.status != BoardCandidateClaim.Status.DRAFT:
            return ClaimResult(
                ok=False,
                code="INVALID_STATUS",
                message="Only draft claims can be discarded.",
            )

        try:
            claim.status = BoardCandidateClaim.Status.DISCARDED
            claim.save()
        except IntegrityError:
            logger.warning(
                "Error discarding Board Candidate Claim for candidate %s, id %s",
                claim.candidate.member.login,
                claim.id,
            )
            return ClaimResult(
                ok=False,
                code="ERROR",
                message="Something went wrong.",
            )
        except ValidationError as e:
            return ClaimResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=json.dumps(e.message_dict),
            )

        return ClaimResult(ok=True, code="SUCCESS", message="Claim discarded successfully.")

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def submit_board_candidate_claim(
        self, info: Info, input_data: SubmitClaimInput
    ) -> ClaimResult:
        """Submit a claim."""
        user = info.context.request.user

        try:
            claim = BoardCandidateClaim.objects.select_for_update().get(
                pk=int(input_data.claim_id.node_id)
            )
        except BoardCandidateClaim.DoesNotExist:
            return ClaimResult(ok=False, code="NOT_FOUND", message="Claim not found.")

        if claim.candidate.member.login != str(user):
            return ClaimResult(ok=False, code="FORBIDDEN", message="Access denied.")

        if claim.status != BoardCandidateClaim.Status.DRAFT:
            return ClaimResult(
                ok=False,
                code="INVALID_STATUS",
                message="Only draft claims can be submitted.",
            )

        if not claim.evidences.filter(is_removed=False).exists():
            return ClaimResult(
                ok=False,
                code="VALIDATION_ERROR",
                message="Claim must have at least one evidence to submit.",
            )

        result = None
        try:
            claim.status = BoardCandidateClaim.Status.SUBMITTED
            claim.save()
        except IntegrityError:
            logger.warning(
                "Error submitting Board Candidate Claim for candidate %s, id %s",
                claim.candidate.member.login,
                claim.id,
            )
            result = ClaimResult(
                ok=False,
                code="ERROR",
                message="Something went wrong.",
            )
        except ValidationError as e:
            result = ClaimResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=json.dumps(e.message_dict),
            )
        else:
            result = ClaimResult(
                ok=True,
                code="SUCCESS",
                message="Claim submitted successfully.",
            )

        return result

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def withdraw_board_candidate_claim(
        self, info: Info, input_data: WithdrawClaimInput
    ) -> ClaimResult:
        """Withdraw a claim."""
        user = info.context.request.user

        try:
            claim = BoardCandidateClaim.objects.select_for_update().get(
                pk=int(input_data.claim_id.node_id)
            )
        except BoardCandidateClaim.DoesNotExist:
            return ClaimResult(ok=False, code="NOT_FOUND", message="Claim not found.")

        if claim.candidate.member.login != str(user):
            return ClaimResult(ok=False, code="FORBIDDEN", message="Access denied.")

        if claim.status not in {
            BoardCandidateClaim.Status.SUBMITTED,
            BoardCandidateClaim.Status.APPROVED,
        }:
            return ClaimResult(
                ok=False,
                code="INVALID_STATUS",
                message="Only submitted or approved claims can be withdrawn.",
            )

        try:
            claim.status = BoardCandidateClaim.Status.WITHDRAWN
            claim.withdrawn_reason = input_data.withdrawn_reason
            claim.withdrawn_at = timezone.now()
            claim.save()
        except IntegrityError:
            logger.warning(
                "Error withdrawing Board Candidate Claim for candidate %s, id %s",
                claim.candidate.member.login,
                claim.id,
            )
            return ClaimResult(
                ok=False,
                code="ERROR",
                message="Something went wrong.",
            )
        except ValidationError as e:
            return ClaimResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=json.dumps(e.message_dict),
            )

        return ClaimResult(ok=True, code="SUCCESS", message="Claim withdrawn successfully.")
