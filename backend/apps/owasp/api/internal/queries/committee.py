"""OWASP committee GraphQL queries."""

import strawberry

from apps.owasp.api.internal.nodes.committee import CommitteeNode
from apps.owasp.models.committee import Committee


@strawberry.type
class CommitteeQuery:
    """Committee queries."""

    @strawberry.field
    def committee(self, key: str) -> CommitteeNode | None:
        """Resolve committee by key.

        Args:
            info: GraphQL execution info.
            key (str): The key of the committee.

        Returns:
            CommitteeNode: The committee object if found, otherwise None.

        """
        try:
            return Committee.objects.get(key=f"www-committee-{key}")
        except Committee.DoesNotExist:
            return None
