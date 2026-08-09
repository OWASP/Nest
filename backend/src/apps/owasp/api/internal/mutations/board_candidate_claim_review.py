"""OWASP Board Candidate Claim Review GraphQL mutations."""

import logging

import pydantic
import strawberry
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from strawberry.types import Info

from apps.common.api.internal.mutations.common import FieldError, validate_pydantic_input
from apps.nest.api.internal.permissions import IsAuthenticated
from apps.nest.models.user import User
from apps.owasp.api.internal.nodes.board_candidate_claim_review import (
    BoardCandidateClaimReviewNode,
)
from apps.owasp.api.internal.nodes.enum import ReviewStatusEnum
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_review import BoardCandidateClaimReview
from apps.owasp.models.board_of_directors import BoardOfDirectors

logger = logging.getLogger(__name__)

ACCESS_DENIED_MSG = "Access denied."
CLAIM_NOT_FOUND_MSG = "Claim not found."
DUPLICATE_REVIEW_MSG = "You have already reviewed this claim."
GENERIC_ERROR_MSG = "Something went wrong."
INVALID_STATUS_MSG = "Review can only be added to submitted claims."


class CreateReviewPydanticInput(pydantic.BaseModel):
    """Pydantic validation for creating a claim review."""

    claim_key: str = pydantic.Field(max_length=100)
    claim_member_login: str
    notes: str = ""
    status: ReviewStatusEnum
    year: int


@strawberry.experimental.pydantic.input(model=CreateReviewPydanticInput, all_fields=True)
class CreateReviewInput:
    """Input for creating claim review."""


@strawberry.type
class ReviewResult:
    """Result for claim review mutations."""

    ok: bool
    code: str | None = None
    message: str | None = None
    review: BoardCandidateClaimReviewNode | None = None
    field_errors: list[FieldError] | None = None


def _validate_review_eligibility(
    claim: BoardCandidateClaim, reviewer: User
) -> ReviewResult | None:
    if claim.status != BoardCandidateClaim.Status.SUBMITTED:
        return ReviewResult(
            ok=False,
            code="INVALID_STATUS",
            message=INVALID_STATUS_MSG,
        )

    if reviewer.github_user and claim.board.get_candidate(login=reviewer.github_user.login):
        return ReviewResult(
            ok=False,
            code="FORBIDDEN",
            message=ACCESS_DENIED_MSG,
        )
    if BoardCandidateClaimReview.objects.filter(claim=claim, reviewer=reviewer).exists():
        return ReviewResult(
            ok=False,
            code="DUPLICATE_REVIEW",
            message=DUPLICATE_REVIEW_MSG,
        )

    return None


@strawberry.type
class BoardCandidateClaimReviewMutations:
    """Board Candidate Claim Review mutations."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    @validate_pydantic_input(ReviewResult)
    def create_board_candidate_claim_review(
        self, info: Info, input_data: CreateReviewInput
    ) -> ReviewResult:
        """Create review for a claim."""
        validated = input_data.validated_data  # type: ignore[attr-defined]
        user = info.context.request.user

        is_reviewer = BoardOfDirectors.objects.filter(
            year=validated.year, claim_reviewers=user
        ).exists()
        if not user.github_user or not is_reviewer:
            return ReviewResult(ok=False, code="FORBIDDEN", message=ACCESS_DENIED_MSG)

        try:
            claim = BoardCandidateClaim.objects.select_for_update().get(
                board__year=validated.year,
                candidate__member__login=validated.claim_member_login,
                key=validated.claim_key,
            )
        except BoardCandidateClaim.DoesNotExist:
            return ReviewResult(ok=False, code="NOT_FOUND", message=CLAIM_NOT_FOUND_MSG)

        result = _validate_review_eligibility(claim, reviewer=user)

        if result:
            return result

        try:
            review = BoardCandidateClaimReview.objects.create(
                claim=claim,
                status=validated.status.value,
                notes=validated.notes,
                reviewer=user,
            )
        except IntegrityError:
            logger.warning(
                "Error creating Board Candidate Claim Review for claim %s of user %s",
                validated.claim_key,
                validated.claim_member_login,
            )
            return ReviewResult(
                ok=False,
                code="ERROR",
                message=GENERIC_ERROR_MSG,
            )
        except ValidationError as e:
            messages = []
            for msgs in e.message_dict.values():
                messages.extend(msgs)
            return ReviewResult(
                ok=False,
                code="VALIDATION_ERROR",
                message=" ".join(messages),
            )

        return ReviewResult(
            ok=True,
            code="SUCCESS",
            message="Review created successfully.",
            review=review,
        )
