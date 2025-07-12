"""GraphQL query for API keys."""

import strawberry

from apps.nest.graphql.nodes.api_key import APIKeyNode
from apps.nest.graphql.permissions import IsAuthenticated
from apps.nest.models import APIKey


@strawberry.type
class APIKeyQueries:
    """GraphQL query class for retrieving API keys."""

    @strawberry.field(permission_classes=[IsAuthenticated])
    def active_api_key_count(self, info) -> int:
        """Return count of active API keys for user."""
        user = info.context.request.user
        return APIKey.active_count_for_user(user)

    @strawberry.field(permission_classes=[IsAuthenticated])
    def api_keys(self, info, *, include_revoked: bool = False) -> list[APIKeyNode]:
        """Resolve API keys for the authenticated user.

        Args:
            info: GraphQL resolver context.
            include_revoked: If True, include revoked API keys in the result.

        Returns:
            list[APIKeyNode]: List of API keys associated with the authenticated user.

        """
        user = info.context.request.user
        keys = APIKey.objects.filter(user=user).order_by("-created_at")
        return keys.filter(is_revoked=include_revoked)
