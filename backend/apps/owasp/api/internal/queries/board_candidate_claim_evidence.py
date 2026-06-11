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
        self, info: strawberry.Info, login: str, key: str
    ) -> list[BoardCandidateClaimEvidenceNode]:
        """Resolve Board Candidate Claim Evidences for a given claim.

        Args:
            info (Info): Strawberry Info.
            login (str): The login of the candidate.
            key (str): The key of the claim.

        Returns:
            List of BoardCandidateClaimEvidenceNode objects

        """
        user = info.context.request.user
        claim = BoardCandidateClaim.objects.filter(cancidate__member__login=login, key=key).first()
        if claim is None:
            return []

        is_self = (
            user.is_authenticated
            and claim.candidate.member is not None
            and user.github_user == claim.candidate.member
        )

        return (
            claim.evidences.filter(is_removed=False)
            if is_self or claim.status == BoardCandidateClaim.Status.APPROVED
            else []
        )
