"""Nest API key GraphQL Mutations."""

from datetime import datetime

import strawberry

from apps.nest.graphql.nodes.api_key import APIKeyNode
from apps.nest.graphql.permissions import IsAuthenticated
from apps.nest.models import APIKey


@strawberry.type
class CreateAPIKeyResult:
    """Result of creating an API key."""

    api_key: APIKeyNode
    raw_key: str


@strawberry.type
class APIKeyMutations:
    """GraphQL mutation class for API keys."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_api_key(
        self, info, name: str, expires_at: datetime | None = None
    ) -> CreateAPIKeyResult:
        """Create a new API key for the authenticated user."""
        user = info.context.request.user

        try:
            instance, raw_key = APIKey.create(user=user, name=name, expires_at=expires_at)
            return CreateAPIKeyResult(api_key=instance, raw_key=raw_key)
        except Exception:
            raise Exception("API key name already exists")

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def revoke_api_key(self, info, key_id: int) -> bool:
        """Revoke an API key for the authenticated user."""
        user = info.context.request.user
        try:
            api_key = APIKey.objects.get(id=key_id, user=user)
            api_key.is_revoked = True
            api_key.save(update_fields=["is_revoked"])
        except APIKey.DoesNotExist:
            return False
        else:
            return True
