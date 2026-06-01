"""OWASP Board Candidate Claim GraphQL mutations."""

import json
import logging

import strawberry
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils import timezone
from strawberry.types import Info

from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.api.internal.nodes.board_candidate_claim import BoardCandidateClaimNode
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


@strawberry.input
class ReorderClaimsInput:
    """Input for reordering claims."""

    claim_ids: list[strawberry.relay.GlobalID]


@strawberry.type
class ReorderClaimsResult:
    """Result for reorder claims mutation."""

    ok: bool
    code: str | None = None
    message: str | None = None
    claims: list[BoardCandidateClaimNode] | None = None


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
                candidate.member.login,
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
        except (BoardCandidateClaim.DoesNotExist, ValueError):
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
        except (BoardCandidateClaim.DoesNotExist, ValueError):
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
        except (BoardCandidateClaim.DoesNotExist, ValueError):
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
        except (BoardCandidateClaim.DoesNotExist, ValueError):
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

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def reorder_board_candidate_claims(
        self, info: Info, input_data: ReorderClaimsInput
    ) -> ReorderClaimsResult:
        """Reorder claims for a candidate in a board year."""
        user = info.context.request.user

        claim_ids = [int(claim_id.node_id) for claim_id in input_data.claim_ids]
        if not claim_ids:
            return ReorderClaimsResult(
                ok=False,
                code="VALIDATION_ERROR",
                message="At least one claim is required for reordering.",
            )
        if len(set(claim_ids)) != len(claim_ids):
            return ReorderClaimsResult(
                ok=False,
                code="VALIDATION_ERROR",
                message="Duplicate claim ids are not allowed.",
            )

        claims_query = BoardCandidateClaim.objects.filter(pk__in=claim_ids)
        if claims_query.count() != len(claim_ids):
            return ReorderClaimsResult(
                ok=False,
                code="NOT_FOUND",
                message="One or more claims were not found.",
            )

        claims = list(
            claims_query.select_for_update(of=("self",)).select_related("candidate__member")
        )
        if any(claim.candidate.member.login != str(user) for claim in claims):
            return ReorderClaimsResult(
                ok=False,
                code="FORBIDDEN",
                message="Access denied.",
            )

        candidate_ids = {claim.candidate_id for claim in claims}
        board_ids = {claim.board_id for claim in claims}
        if len(candidate_ids) != 1 or len(board_ids) != 1:
            return ReorderClaimsResult(
                ok=False,
                code="VALIDATION_ERROR",
                message="All claims must belong to the same candidate and board year.",
            )

        id_to_order = {claim_id: idx for idx, claim_id in enumerate(claim_ids)}
        for claim in claims:
            claim.order = id_to_order[claim.id]

        BoardCandidateClaim.objects.bulk_update(claims, ["order"])

        ordered_claims = (
            BoardCandidateClaim.objects.filter(pk__in=claim_ids)
            .select_related("candidate__member", "board")
            .order_by("order", "nest_created_at")
        )

        return ReorderClaimsResult(
            ok=True,
            code="SUCCESS",
            message="Claims reordered successfully.",
            claims=list(ordered_claims),
        )
