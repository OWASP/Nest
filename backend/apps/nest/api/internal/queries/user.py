"""GraphQL queries for Nest users."""

import strawberry

from apps.nest.api.internal.nodes.user import AuthUserNode
from apps.nest.api.internal.permissions import IsAuthenticated


@strawberry.type
class UserQueries:
    """Queries to fetch user information."""

    @strawberry.field(permission_classes=[IsAuthenticated])
    def me(self, info) -> AuthUserNode:
        """Return the authenticated user."""
        return info.context.request.user
