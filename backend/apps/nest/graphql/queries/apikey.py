"""GraphQL query for API keys."""

import strawberry

from apps.nest.graphql.nodes.apikey import APIKeyNode
from apps.nest.graphql.utils import get_authenticated_user
from apps.nest.models import APIKey


@strawberry.type
class APIKeyQueries:
    """GraphQL query class for retrieving API keys."""

    @strawberry.field
    def api_keys(self, info, *, include_revoked: bool = False) -> list[APIKeyNode]:
        """Resolve API keys for the authenticated user.

        Args:
            info: GraphQL resolver context.
            include_revoked: If True, include revoked API keys in the result.

        Returns:
            list[APIKeyNode]: List of API keys associated with the authenticated user.

        """
        request = info.context.request
        user = get_authenticated_user(request)
        keys = APIKey.objects.filter(user=user).order_by("-created_at")
        return keys.filter(revoked=include_revoked)
