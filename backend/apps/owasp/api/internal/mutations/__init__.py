"""OWASP app mutations."""

import strawberry

from .board_candidate_claim import BoardCandidateClaimMutations


@strawberry.type
class OwaspMutation(BoardCandidateClaimMutations):
    """OWASP mutations."""
