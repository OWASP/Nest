"""GraphQL queries for API keys."""

import strawberry
from strawberry.directive import DirectiveValue
from strawberry.types import Info

from apps.nest.graphql.nodes.api_key import ApiKeyNode
from apps.nest.graphql.permissions import IsAuthenticated
from apps.nest.models import ApiKey


@strawberry.type
class ApiKeyQueries:
    """GraphQL query class for retrieving API keys."""

    @strawberry.field(permission_classes=[IsAuthenticated])
    def active_api_key_count(self, info: Info) -> int:
        """Return count of active API keys for user."""
        return info.context.request.user.active_api_keys.count()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def api_keys(
        self, info: Info, *, include_revoked: DirectiveValue[bool] = False
    ) -> list[ApiKeyNode]:
        """Resolve API keys for the authenticated user.

        Args:
            info: GraphQL resolver context.
            include_revoked: If True, include revoked API keys in the result.

        Returns:
            list[APIKeyNode]: List of API keys associated with the authenticated user.

        """
        return ApiKey.objects.filter(
            is_revoked=include_revoked,
            user=info.context.request.user,
        ).order_by("-created_at")
