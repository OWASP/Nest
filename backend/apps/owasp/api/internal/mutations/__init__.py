"""OWASP app mutations."""

import strawberry

from .board_candidate_claim import BoardCandidateClaimMutations
from .board_candidate_claim_evidence import BoardCandidateClaimEvidenceMutations


@strawberry.type
class OwaspMutation(BoardCandidateClaimMutations, BoardCandidateClaimEvidenceMutations):
    """OWASP mutations."""
