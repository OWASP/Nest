"""GraphQL queries for API keys."""

import strawberry
from strawberry.types import Info

from apps.api.internal.nodes.api_key import ApiKeyNode
from apps.nest.api.internal.permissions import IsAuthenticated


@strawberry.type
class ApiKeyQueries:
    """GraphQL query class for retrieving API keys."""

    @strawberry.field(permission_classes=[IsAuthenticated])
    def active_api_key_count(self, info: Info) -> int:
        """Return count of active API keys for user."""
        return info.context.request.user.active_api_keys.count()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def api_keys(self, info: Info) -> list[ApiKeyNode]:
        """Resolve API keys for the authenticated user.

        Args:
            info: GraphQL resolver context.

        Returns:
            list[ApiKeyNode]: List of API keys associated with the authenticated user.

        """
        return info.context.request.user.active_api_keys.order_by("-created_at")
