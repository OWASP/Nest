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
            board__year=year,
            candidate__member__login=login,
        ).order_by("order", "nest_created_at")

        if not is_self:
            claims = claims.filter(status=BoardCandidateClaim.Status.APPROVED)

        return claims

    @strawberry_django.field
    def board_candidate_claim(
        self, info: strawberry.Info, key: str, login: str, year: int
    ) -> BoardCandidateClaimNode | None:
        """Resolve Board Candidate Claim.

        Args:
            info (Info): Strawberry Info.
            key (str): The key of the claim.
            login (str): The login of the candidate.
            year (int): The year of the election.

        Returns:
            BoardCandidateClaimNode object if found, None otherwise.

        """
        try:
            claim = BoardCandidateClaim.objects.get(
                board__year=year,
                candidate__member__login=login,
                key=key,
            )
        except BoardCandidateClaim.DoesNotExist:
            return None

        user = info.context.request.user
        is_self = (
            user.is_authenticated
            and user.github_user is not None
            and user.github_user == claim.candidate.member
        )

        return claim if is_self or claim.status == BoardCandidateClaim.Status.APPROVED else None
