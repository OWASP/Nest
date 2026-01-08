"""OWASP Board of Directors GraphQL queries."""

import strawberry

from apps.owasp.api.internal.nodes.board_of_directors import BoardOfDirectorsNode
from apps.owasp.models.board_of_directors import BoardOfDirectors

MAX_LIMIT = 1000


@strawberry.type
class BoardOfDirectorsQuery:
    """GraphQL queries for Board of Directors model."""

    @strawberry.field
    def board_of_directors(self, year: int) -> BoardOfDirectorsNode | None:
        """Resolve Board of Directors by year.

        Args:
            year: The election year

        Returns:
            BoardOfDirectorsNode or None if not found

        """
        try:
            return BoardOfDirectors.objects.get(year=year)
        except BoardOfDirectors.DoesNotExist:
            return None

    @strawberry.field
    def boards_of_directors(self, limit: int = 10) -> list[BoardOfDirectorsNode]:
        """Resolve multiple Board of Directors instances.

        Args:
            limit: Maximum number of boards to return.

        Returns:
            List of BoardOfDirectorsNode objects.

        """
        return (
            BoardOfDirectors.objects.order_by("-year")[:limit]
            if (limit := min(limit, MAX_LIMIT)) > 0
            else []
        )
