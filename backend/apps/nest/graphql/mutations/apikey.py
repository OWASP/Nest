"""Nest API key GraphQL Mutations."""

import strawberry

from apps.nest.graphql.nodes.apikey import APIKeyNode
from apps.nest.graphql.utils import get_authenticated_user
from apps.nest.models import APIKey


@strawberry.type
class CreateAPIKeyResult:
    """Result of creating an API key."""

    api_key: APIKeyNode
    raw_key: str


@strawberry.type
class APIKeyMutations:
    """GraphQL mutation class for API keys."""

    @strawberry.mutation
    def create_api_key(self, info, name: str, expires_at: str | None = None) -> CreateAPIKeyResult:
        """Create a new API key for the authenticated user."""
        request = info.context.request
        user = get_authenticated_user(request)
        instance, raw_key = APIKey.create(user=user, name=name, expires_at=expires_at)
        return CreateAPIKeyResult(api_key=instance, raw_key=raw_key)

    @strawberry.mutation
    def revoke_api_key(self, info, key_id: int) -> bool:
        """Revoke an API key for the authenticated user."""
        request = info.context.request
        user = get_authenticated_user(request)
        try:
            api_key = APIKey.objects.get(id=key_id, user=user)
            api_key.revoked = True
            api_key.save(update_fields=["revoked"])
        except APIKey.DoesNotExist:
            return False
        else:
            return True
