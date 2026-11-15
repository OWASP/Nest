"""OWASP committee GraphQL queries."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.committee import CommitteeNode
from apps.owasp.models.committee import Committee


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
