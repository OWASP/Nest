"""GraphQL node for APIKey model."""

import strawberry_django

from apps.nest.models import ApiKey


@strawberry_django.type(
    ApiKey,
    fields=[
        "created_at",
        "is_revoked",
        "expires_at",
        "name",
        "public_id",
    ],
)
class ApiKeyNode:
    """GraphQL node for API keys."""
