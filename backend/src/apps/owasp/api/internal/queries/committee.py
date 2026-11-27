"""OWASP committee GraphQL queries."""

import strawberry
import strawberry_django

from apps.common.constants import (
    MAX_SEARCH_QUERY_LENGTH,
    MIN_SEARCH_QUERY_LENGTH,
)
from apps.owasp.api.internal.nodes.committee import CommitteeNode
from apps.owasp.models.committee import Committee

SEARCH_COMMITTEES_LIMIT = 3


@strawberry.type
class CommitteeQuery:
    """Committee queries."""

    @strawberry_django.field
    def committee(self, key: str) -> CommitteeNode | None:
        """Resolve committee by key.

        Args:
            info: GraphQL execution info.
            key (str): The key of the committee.

        Returns:
            CommitteeNode: The committee object if found, otherwise None.

        """
        return Committee.get_by_key(key)

    @strawberry_django.field
    def search_committees(self, query: str) -> list[CommitteeNode]:
        """Search active committees by name (case-insensitive, partial match)."""
        cleaned_query = query.strip()
        if (
            len(cleaned_query) < MIN_SEARCH_QUERY_LENGTH
            or len(cleaned_query) > MAX_SEARCH_QUERY_LENGTH
        ):
            return []

        return (
            Committee.active_committees.select_related(
                "owasp_repository",
            )
            .filter(
                name__icontains=cleaned_query,
            )
            .order_by("name")[:SEARCH_COMMITTEES_LIMIT]
        )
