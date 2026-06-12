"""OWASP Board Candidate Claim Evidence GraphQL queries."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.board_candidate_claim_evidence import (
    BoardCandidateClaimEvidenceNode,
)
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


@strawberry.type
class BoardCandidateClaimEvidenceQuery:
    """GraphQL queries for Board Candidate Claim Evidence model."""

    @strawberry_django.field
    def board_candidate_claim_evidences(
        self, info: strawberry.Info, claim_id: strawberry.relay.GlobalID
    ) -> list[BoardCandidateClaimEvidenceNode]:
        """Resolve Board Candidate Claim Evidences for a given claim.

        Args:
            info (Info): Strawberry Info.
            claim_id (GlobalID): The id of the claim.

        Returns:
            List of BoardCandidateClaimEvidenceNode objects

        """
        user = info.context.request.user
        try:
            claim = BoardCandidateClaim.objects.filter(pk=claim_id.node_id).first()
        except (ValueError, TypeError):
            return []
        if claim is None:
            return []

        is_self = (
            user.is_authenticated
            and claim.candidate.member is not None
            and user.github_user == claim.candidate.member
        )

        if not is_self and claim.status != BoardCandidateClaim.Status.APPROVED:
            return []

        return claim.evidences.filter(is_removed=False)
