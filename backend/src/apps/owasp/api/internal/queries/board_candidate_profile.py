"""OWASP Board Candidate Profile GraphQL queries."""

import strawberry
import strawberry_django
from django.contrib.contenttypes.models import ContentType

from apps.owasp.api.internal.nodes.board_candidate_profile import BoardCandidateProfileNode
from apps.owasp.models.board_candidate_profile import BoardCandidateProfile
from apps.owasp.models.board_of_directors import BoardOfDirectors


@strawberry.type
class BoardCandidateProfileQuery:
    """GraphQL queries for Board Candidate Profile model."""

    @strawberry_django.field
    def board_candidate_profile(
        self, info: strawberry.Info, login: str, year: int
    ) -> BoardCandidateProfileNode | None:
        """Resolve Board Candidate Profile.

        Args:
            info (Info): Strawberry Info.
            login (str): The login of the candidate.
            year (int): The year of the election.

        Returns:
            BoardCandidateProfileNode object if found, None otherwise.

        """
        try:
            board = BoardOfDirectors.objects.get(year=year)
            content_type = ContentType.objects.get_for_model(BoardOfDirectors)
            return BoardCandidateProfile.objects.select_related("candidate__member").get(
                candidate__member__login=login,
                candidate__entity_type=content_type,
                candidate__entity_id=board.id,
            )
        except (BoardOfDirectors.DoesNotExist, BoardCandidateProfile.DoesNotExist):
            return None
