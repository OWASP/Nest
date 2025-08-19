"""GraphQL queries for badges."""

import strawberry
import strawberry_django

from apps.nest.api.internal.nodes.badge import BadgeNode
from apps.nest.models import Badge


@strawberry.type
class BadgeQueries:
    """GraphQL query class for retrieving badges."""

    @strawberry_django.field
    def badges(self) -> list[BadgeNode]:
        """Return all badges sorted by weight then name."""
        return Badge.objects.all().order_by("weight", "name")
