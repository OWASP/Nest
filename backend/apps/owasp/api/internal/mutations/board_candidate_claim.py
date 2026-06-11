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

ACCESS_DENIED_MSG = "Access denied."
CLAIM_NOT_FOUND_MSG = "Claim not found."
GENERIC_ERROR_MSG = "Something went wrong."


@strawberry.input
class CreateClaimInput:
    """Input for creating a claim."""

    description: str
    name: str
    year: int


@strawberry.input
class UpdateClaimInput:
    """Input for updating a claim."""

    description: str | None = None
    key: str
    name: str | None = None


@strawberry.input
class DiscardClaimInput:
    """Input for discarding a claim."""

    key: str


@strawberry.input
class SubmitClaimInput:
    """Input for submitting a claim."""

    key: str


@strawberry.input
class WithdrawClaimInput:
    """Input for withdrawing a claim."""

    key: str
    withdrawn_reason: str


@strawberry.input
class ReorderClaimsInput:
    """Input for reordering claims."""

    keys: list[str]


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


def _validate_reorder_claims(
    login: str,
    input_data: ReorderClaimsInput,
) -> tuple[list[str], ReorderClaimsResult | None]:
    """Validate reorder claims input.

    Args:
        login (str): The login of the candidate.
        input_data (ReorderClaimsInput): Input containing claim keys to reorder.

    Returns:
        tuple of (list[str], ReorderClaimsResult | None)

    """
    keys = input_data.keys
    if not keys:
        return keys, ReorderClaimsResult(
            ok=False,
            code="VALIDATION_ERROR",
            message="At least one claim is required for reordering.",
        )

    if len(set(keys)) != len(keys):
        return keys, ReorderClaimsResult(
            ok=False,
            code="VALIDATION_ERROR",
            message="Duplicate claim keys are not allowed.",
        )

    if BoardCandidateClaim.objects.filter(
        candidate__member__login=login, key__in=keys
    ).count() != len(keys):
        return keys, ReorderClaimsResult(
            ok=False,
            code="NOT_FOUND",
            message="One or more claims were not found.",
        )

    return keys, None


@strawberry.type
class BoardCandidateClaimMutations:
    """Board Candidate Claim mutations."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def create_board_candidate_claim(
        self, info: Info, input_data: CreateClaimInput
    ) -> ClaimResult:
        """Create a new draft claim for a candidate."""
        user = info.context.request.user
        try:
            board = BoardOfDirectors.objects.get(year=input_data.year)
        except BoardOfDirectors.DoesNotExist:
            return ClaimResult(
                ok=False,
                code="NOT_FOUND",
                message=f"No board election found for the year {input_data.year}.",
            )

        if user.github_user is None:
            return ClaimResult(ok=False, code="FORBIDDEN", message=ACCESS_DENIED_MSG)

        candidate = board.get_candidate(login=user.github_user.login)
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
                name=input_data.name,
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
                message=GENERIC_ERROR_MSG,
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
                candidate__member__login=user.github_user.login, key=input_data.key
            )
        except BoardCandidateClaim.DoesNotExist:
            return ClaimResult(ok=False, code="NOT_FOUND", message=CLAIM_NOT_FOUND_MSG)

        if claim.is_locked:
            return ClaimResult(ok=False, code="LOCKED", message="Cannot update a locked claim.")

        update_fields = []
        if input_data.name:
            claim.name = input_data.name
            update_fields.append("name")
        if input_data.description:
            claim.description = input_data.description
            update_fields.append("description")

        try:
            claim.save(update_fields=update_fields)
        except IntegrityError:
            logger.warning(
                "Error updating Board Candidate Claim for candidate %s, key %s",
                claim.candidate.member.login,
                input_data.key,
            )
            return ClaimResult(
                ok=False,
                code="ERROR",
                message=GENERIC_ERROR_MSG,
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
                candidate__member__login=user.github_user.login, key=input_data.key
            )
        except BoardCandidateClaim.DoesNotExist:
            return ClaimResult(ok=False, code="NOT_FOUND", message=CLAIM_NOT_FOUND_MSG)

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
                "Error discarding Board Candidate Claim for candidate %s, key %s",
                claim.candidate.member.login,
                claim.key,
            )
            return ClaimResult(
                ok=False,
                code="ERROR",
                message=GENERIC_ERROR_MSG,
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
                candidate__member__login=user.github_user.login, key=input_data.key
            )
        except BoardCandidateClaim.DoesNotExist:
            return ClaimResult(ok=False, code="NOT_FOUND", message=CLAIM_NOT_FOUND_MSG)

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
                "Error submitting Board Candidate Claim for candidate %s, key %s",
                claim.candidate.member.login,
                claim.key,
            )
            result = ClaimResult(
                ok=False,
                code="ERROR",
                message=GENERIC_ERROR_MSG,
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
                candidate__member__login=user.github_user.login, key=input_data.key
            )
        except BoardCandidateClaim.DoesNotExist:
            return ClaimResult(ok=False, code="NOT_FOUND", message=CLAIM_NOT_FOUND_MSG)

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
                "Error withdrawing Board Candidate Claim for candidate %s, key %s",
                claim.candidate.member.login,
                claim.key,
            )
            return ClaimResult(
                ok=False,
                code="ERROR",
                message=GENERIC_ERROR_MSG,
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
        login = user.github_user.login

        keys, error = _validate_reorder_claims(login, input_data)
        if error:
            return error

        claims = list(
            BoardCandidateClaim.objects.filter(candidate__member__login=login, key__in=keys)
            .select_for_update(of=("self",))
            .select_related("candidate__member")
        )

        candidate_ids = {claim.candidate_id for claim in claims}
        board_ids = {claim.board_id for claim in claims}
        if len(candidate_ids) != 1 or len(board_ids) != 1:
            return ReorderClaimsResult(
                ok=False,
                code="VALIDATION_ERROR",
                message="All claims must belong to the same candidate and board year.",
            )

        keys_to_order = {key: idx for idx, key in enumerate(keys)}
        for claim in claims:
            claim.order = keys_to_order[claim.key]

        if any(
            claim.status
            not in {
                BoardCandidateClaim.Status.DRAFT,
                BoardCandidateClaim.Status.APPROVED,
            }
            for claim in claims
        ):
            return ReorderClaimsResult(
                ok=False,
                code="VALIDATION_ERROR",
                message="Only draft and approved claims can be reordered.",
            )

        BoardCandidateClaim.objects.bulk_update(claims, ["order"])

        ordered_claims = (
            BoardCandidateClaim.objects.filter(candidate__member__login=login, key__in=keys)
            .select_related("candidate__member", "board")
            .order_by("order", "nest_created_at")
        )

        return ReorderClaimsResult(
            ok=True,
            code="SUCCESS",
            message="Claims reordered successfully.",
            claims=list(ordered_claims),
        )
