"""GraphQL node for APIKey model."""

import strawberry_django

from apps.nest.models import APIKey


@strawberry_django.type(
    APIKey, fields=["id", "name", "is_revoked", "created_at", "expires_at", "key_suffix"]
)
class APIKeyNode:
    """GraphQL node for API keys."""
