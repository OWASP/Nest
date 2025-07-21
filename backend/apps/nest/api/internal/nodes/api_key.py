"""GraphQL node for ApiKey model."""

import strawberry_django

from apps.nest.models.api_key import ApiKey


@strawberry_django.type(
    ApiKey,
    fields=[
        "created_at",
        "is_revoked",
        "expires_at",
        "name",
        "uuid",
    ],
)
class ApiKeyNode:
    """GraphQL node for API keys."""
