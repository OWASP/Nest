"""GraphQL queries for Badge model."""

import strawberry

from apps.nest.api.internal.nodes.badge import BadgeNode
from apps.nest.models.badge import Badge


@strawberry.type
class BadgeQueries:
    """GraphQL query class for badges."""

    @strawberry.field
    def badges(self) -> list[BadgeNode]:
        """Return badges."""
        return Badge.objects.order_by("weight", "name")
