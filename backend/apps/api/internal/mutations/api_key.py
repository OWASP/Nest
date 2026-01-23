"""API app mutations."""

import logging
from datetime import datetime
from uuid import UUID

import strawberry
from django.db.utils import IntegrityError
from django.utils import timezone
from strawberry.types import Info

from apps.api.internal.nodes.api_key import ApiKeyNode
from apps.api.models.api_key import MAX_ACTIVE_KEYS, MAX_WORD_LENGTH, ApiKey
from apps.nest.api.internal.permissions import IsAuthenticated

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
    """API key mutations."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_api_key(self, info: Info, name: str, expires_at: datetime) -> CreateApiKeyResult:
        """Create a new API key for the authenticated user."""
        if not name or not name.strip():
            return CreateApiKeyResult(ok=False, code="INVALID_NAME", message="Name is required")

        if len(name.strip()) > MAX_WORD_LENGTH:
            return CreateApiKeyResult(ok=False, code="INVALID_NAME", message="Name too long")

        if expires_at <= timezone.now():
            return CreateApiKeyResult(
                ok=False, code="INVALID_DATE", message="Expiry date must be in future"
            )

        try:
            if not (
                result := ApiKey.create(
                    expires_at=expires_at,
                    name=name,
                    user=info.context.request.user,
                )
            ):
                return CreateApiKeyResult(
                    ok=False,
                    code="LIMIT_REACHED",
                    message=f"You can have at most {MAX_ACTIVE_KEYS} active API keys.",
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
            # Reason: Logging the error message string only, not the sensitive API key credential itself. # noqa: E501
            logger.warning(  # nosemgrep: python.lang.security.audit.logging.logger-credential-leak.python-logger-credential-disclosure  # noqa: E501
                "Error creating API key: %s", err
            )
            return CreateApiKeyResult(
                ok=False,
                code="ERROR",
                message="Something went wrong.",
            )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def revoke_api_key(self, info: Info, uuid: UUID) -> RevokeApiKeyResult:
        """Revoke an API key for the authenticated user."""
        try:
            api_key = ApiKey.objects.get(
                uuid=uuid,
                user=info.context.request.user,
            )
            api_key.is_revoked = True
            api_key.save(update_fields=("is_revoked", "updated_at"))
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
