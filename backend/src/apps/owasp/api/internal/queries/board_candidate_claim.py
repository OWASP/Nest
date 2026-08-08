"""OWASP Board Candidate Claim GraphQL queries."""

import strawberry
import strawberry_django
from django.db.models import Exists, OuterRef, Q

from apps.owasp.api.internal.nodes.board_candidate_claim import BoardCandidateClaimNode
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence
from apps.owasp.models.board_of_directors import BoardOfDirectors


@strawberry.type
class BoardCandidateClaimQuery:
    """GraphQL queries for Board Candidate Claim model."""

    @strawberry_django.field
    def board_candidate_claims(
        self, info: strawberry.Info, year: int, login: str | None = None
    ) -> list[BoardCandidateClaimNode]:
        """Resolve Board Candidate Claims for a given candidate and year.

        Args:
            info (Info): Strawberry Info.
            login (str, optional): The login of the candidate.
            year (int): The year of the elections.

        Returns:
            List of BoardCandidateClaimNode objects

        """
        user = info.context.request.user
        is_reviewer = (
            user.is_authenticated
            and BoardOfDirectors.objects.filter(year=year, reviewers=user).exists()
        )
        claims = BoardCandidateClaim.objects.filter(
            board__year=year,
        )

        if login is not None:
            is_self = (
                user.is_authenticated
                and user.github_user is not None
                and user.github_user.login == login
            )
            claims = claims.filter(candidate__member__login=login)

            if not is_self and not is_reviewer:
                claims = claims.filter(
                    status__in=[
                        BoardCandidateClaim.Status.APPROVED,
                        BoardCandidateClaim.Status.REJECTED,
                    ]
                )
            elif is_reviewer and not is_self:
                claims = claims.filter(
                    status__in=[
                        BoardCandidateClaim.Status.SUBMITTED,
                        BoardCandidateClaim.Status.APPROVED,
                        BoardCandidateClaim.Status.REJECTED,
                    ]
                )
        elif is_reviewer:
            claims = claims.filter(
                Q(candidate__member=user.github_user)
                | Q(
                    status__in=[
                        BoardCandidateClaim.Status.SUBMITTED,
                        BoardCandidateClaim.Status.APPROVED,
                        BoardCandidateClaim.Status.REJECTED,
                    ]
                )
            )
        elif user.is_authenticated and user.github_user:
            claims = claims.filter(
                Q(candidate__member=user.github_user)
                | Q(
                    status__in=[
                        BoardCandidateClaim.Status.APPROVED,
                        BoardCandidateClaim.Status.REJECTED,
                    ]
                )
            )
        else:
            claims = claims.filter(
                status__in=[
                    BoardCandidateClaim.Status.APPROVED,
                    BoardCandidateClaim.Status.REJECTED,
                ]
            )

        return (
            claims.annotate(
                evidence_exists=Exists(
                    BoardCandidateClaimEvidence.objects.filter(
                        claim=OuterRef("pk"), is_removed=False
                    )
                ),
            )
            .select_related("candidate__member")
            .order_by("order", "nest_created_at")
        )

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
            claim = (
                BoardCandidateClaim.objects.select_related("candidate__member", "board")
                .annotate(
                    evidence_exists=Exists(
                        BoardCandidateClaimEvidence.objects.filter(
                            claim=OuterRef("pk"), is_removed=False
                        )
                    ),
                )
                .get(
                    board__year=year,
                    candidate__member__login=login,
                    key=key,
                )
            )
        except BoardCandidateClaim.DoesNotExist:
            return None

        user = info.context.request.user
        is_self = (
            user.is_authenticated
            and user.github_user is not None
            and user.github_user == claim.candidate.member
        )
        is_reviewer = user.is_authenticated and claim.board.reviewers.filter(id=user.id).exists()

        return (
            claim
            if (
                is_self
                or (is_reviewer and claim.status == BoardCandidateClaim.Status.SUBMITTED)
                or claim.status
                in {
                    BoardCandidateClaim.Status.APPROVED,
                    BoardCandidateClaim.Status.REJECTED,
                }
            )
            else None
        )
