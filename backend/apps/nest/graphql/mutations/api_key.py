"""Nest API key GraphQL Mutations."""

import logging
from datetime import datetime

import strawberry
from django.db.utils import IntegrityError

from apps.nest.graphql.nodes.api_key import APIKeyNode
from apps.nest.graphql.permissions import IsAuthenticated
from apps.nest.models import APIKey

logger = logging.getLogger(__name__)


@strawberry.type
class RevokeAPIKeyResult:
    """Payload for API key revocation result."""

    ok: bool
    code: str | None = None
    message: str | None = None


@strawberry.type
class CreateAPIKeyResult:
    """Result of creating an API key."""

    api_key: APIKeyNode | None
    raw_key: str | None


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
        except IntegrityError as err:
            logger.warning("Error creating API key: %s", err)
            return CreateAPIKeyResult(api_key=None, raw_key=None)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def revoke_api_key(self, info, key_id: int) -> RevokeAPIKeyResult:
        """Revoke an API key for the authenticated user."""
        user = info.context.request.user
        try:
            api_key = APIKey.objects.get(id=key_id, user=user)
            api_key.is_revoked = True
            api_key.save(update_fields=["is_revoked"])
        except APIKey.DoesNotExist:
            logger.warning("API Key does not exist")
            return RevokeAPIKeyResult(
                ok=False,
                code="NOT_FOUND",
                message="API key not found.",
            )
        else:
            return RevokeAPIKeyResult(
                ok=True, code="SUCCESS", message="API key revoked successfully."
            )
