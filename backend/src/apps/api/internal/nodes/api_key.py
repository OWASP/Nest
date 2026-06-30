"""GraphQL node for ApiKey model."""

import strawberry
import strawberry_django

from apps.api.models.api_key import ApiKey


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
class ApiKeyNode(strawberry.relay.Node):
    """GraphQL node for API keys."""
