"""GraphQL enum for OWASP App."""

import enum

import strawberry

from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_review import BoardCandidateClaimReview


@strawberry.enum
class ClaimStatusEnum(enum.Enum):
    """claim status enum."""

    DRAFT = BoardCandidateClaim.Status.DRAFT
    DISCARDED = BoardCandidateClaim.Status.DISCARDED
    SUBMITTED = BoardCandidateClaim.Status.SUBMITTED
    APPROVED = BoardCandidateClaim.Status.APPROVED
    REJECTED = BoardCandidateClaim.Status.REJECTED
    WITHDRAWN = BoardCandidateClaim.Status.WITHDRAWN


@strawberry.enum
class ReviewDecisionEnum(enum.Enum):
    """Review decision enum."""

    APPROVED = BoardCandidateClaimReview.Decision.APPROVED
    REJECTED = BoardCandidateClaimReview.Decision.REJECTED
