"""OWASP Board Candidate Claim GraphQL queries."""

import strawberry
import strawberry_django

from apps.common.utils import normalize_limit
from apps.owasp.api.internal.nodes.board_candidate_claim import BoardCandidateClaimNode
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim

MAX_LIMIT = 100


@strawberry.type
class BoardCandidateClaimQuery:
    """GraphQL queries for BoardCandidateClaim model."""

    @strawberry_django.field
    def board_candidate_claim(self, key: str) -> BoardCandidateClaimNode | None:
        """Resolve Board Candidate Claim by key.

        Args:
            key: The unique claim key.

        Returns:
            BoardCandidateClaimNode or None if not found.

        """
        try:
            return BoardCandidateClaim.objects.get(key=key)
        except BoardCandidateClaim.DoesNotExist:
            return None

    @strawberry_django.field
    def board_candidate_claims(self, limit: int = 10) -> list[BoardCandidateClaimNode]:
        """Resolve multiple Board Candidate Claims.

        Args:
            limit: Maximum number of claims to return.

        Returns:
            List of BoardCandidateClaimNode objects.

        """
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        return BoardCandidateClaim.objects.order_by("-created_at")[:normalized_limit]
