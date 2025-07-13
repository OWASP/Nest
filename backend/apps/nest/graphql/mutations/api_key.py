"""Nest API key GraphQL Mutations."""

import logging
from datetime import datetime
from uuid import UUID

import strawberry
from django.db.utils import IntegrityError
from strawberry.types import Info

from apps.nest.graphql.nodes.api_key import ApiKeyNode
from apps.nest.graphql.permissions import IsAuthenticated
from apps.nest.models import ApiKey

logger = logging.getLogger(__name__)


@strawberry.type
class RevokeApiKeyResult:
    """Payload for API key revocation result."""

    ok: bool
    code: str | None = None
    message: str | None = None


@strawberry.type
class CreateApiKeyResult:
    """Result of creating an API key."""

    ok: bool
    api_key: ApiKeyNode | None = None
    raw_key: str | None = None
    code: str | None = None
    message: str | None = None


@strawberry.type
class ApiKeyMutations:
    """GraphQL mutation class for API keys."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_api_key(self, info: Info, name: str, expires_at: datetime) -> CreateApiKeyResult:
        """Create a new API key for the authenticated user."""
        user = info.context.request.user

        try:
            result = ApiKey.create(user=user, name=name, expires_at=expires_at)
            if result is None:
                return CreateApiKeyResult(
                    ok=False,
                    code="LIMIT_REACHED",
                    message="You can have at most 5 active API keys.",
                )
            instance, raw_key = result
            return CreateApiKeyResult(
                ok=True,
                api_key=instance,
                raw_key=raw_key,
                code="SUCCESS",
                message="API key created successfully.",
            )
        except IntegrityError as err:
            logger.warning("Error creating API key: %s", err)
            return CreateApiKeyResult(
                ok=False,
                code="ERROR",
                message="Something went wrong.",
            )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def revoke_api_key(self, info: Info, public_id: UUID) -> RevokeApiKeyResult:
        """Revoke an API key for the authenticated user."""
        user = info.context.request.user
        try:
            api_key = ApiKey.objects.get(public_id=public_id, user=user)
            api_key.is_revoked = True
            api_key.save(update_fields=["is_revoked"])
        except ApiKey.DoesNotExist:
            logger.warning("API Key does not exist")
            return RevokeApiKeyResult(
                ok=False,
                code="NOT_FOUND",
                message="API key not found.",
            )
        else:
            return RevokeApiKeyResult(
                ok=True, code="SUCCESS", message="API key revoked successfully."
            )
