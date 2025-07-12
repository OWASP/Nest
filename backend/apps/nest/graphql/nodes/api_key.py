"""GraphQL node for APIKey model."""

import strawberry_django

from apps.nest.models import ApiKey


@strawberry_django.type(
    ApiKey,
    fields=[
        "id",
        "name",
        "is_revoked",
        "created_at",
        "expires_at",
        "key_suffix",
    ],
)
class ApiKeyNode:
    """GraphQL node for API keys."""
