"""OWASP Board Candidate Claim GraphQL queries."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.board_candidate_claim import BoardCandidateClaimNode
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


@strawberry.type
class BoardCandidateClaimQuery:
    """GraphQL queries for Board Candidate Claim model."""

    @strawberry_django.field
    def board_candidate_claims(
        self, info: strawberry.Info, login: str, year: int
    ) -> list[BoardCandidateClaimNode]:
        """Resolve Board Candidate Claims for a given candidate and year.

        Args:
            info (Info): Strawberry Info.
            login (str): The login of the candidate.
            year (int): The year of the elections.

        Returns:
            List of BoardCandidateClaimNode objects

        """
        user = info.context.request.user
        is_self = (
            user.is_authenticated
            and user.github_user is not None
            and user.github_user.login == login
        )
        claims = BoardCandidateClaim.objects.filter(
            candidate__member__login=login,
            board__year=year,
        ).order_by("order", "nest_created_at")

        if not is_self:
            claims = claims.filter(status=BoardCandidateClaim.Status.APPROVED)

        return claims

    @strawberry_django.field
    def board_candidate_claim(
        self, info: strawberry.Info, claim_id: strawberry.relay.GlobalID
    ) -> BoardCandidateClaimNode | None:
        """Resolve Board Candidate Claim for a given claim ID.

        Args:
            info (Info): Strawberry Info.
            claim_id (GlobalID): The id of the claim.

        Returns:
            BoardCandidateClaimNode object if found, None otherwise.

        """
        try:
            claim = BoardCandidateClaim.objects.get(pk=claim_id.node_id)
        except (BoardCandidateClaim.DoesNotExist, ValueError):
            return None

        user = info.context.request.user
        is_self = (
            user.is_authenticated
            and user.github_user is not None
            and user.github_user == claim.candidate.member
        )

        return claim if is_self or claim.status == BoardCandidateClaim.Status.APPROVED else None
