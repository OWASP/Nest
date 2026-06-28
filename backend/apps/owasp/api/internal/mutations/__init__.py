"""OWASP app mutations."""

import strawberry

from .board_candidate_claim import BoardCandidateClaimMutations
from .board_candidate_claim_evidence import BoardCandidateClaimEvidenceMutations
from .board_candidate_claim_review import BoardCandidateClaimReviewMutations


@strawberry.type
class OwaspMutation(
    BoardCandidateClaimMutations,
    BoardCandidateClaimEvidenceMutations,
    BoardCandidateClaimReviewMutations,
):
    """OWASP mutations."""
