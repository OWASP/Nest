"""GraphQL enum for OWASP App."""

import enum

import strawberry

from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


@strawberry.enum
class ClaimStatusEnum(enum.Enum):
    """claim status enum."""

    DRAFT = BoardCandidateClaim.Status.DRAFT
    DISCARDED = BoardCandidateClaim.Status.DISCARDED
    SUBMITTED = BoardCandidateClaim.Status.SUBMITTED
    APPROVED = BoardCandidateClaim.Status.APPROVED
    REJECTED = BoardCandidateClaim.Status.REJECTED
    WITHDRAWN = BoardCandidateClaim.Status.WITHDRAWN
