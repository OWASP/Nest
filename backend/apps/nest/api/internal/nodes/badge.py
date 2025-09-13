"""GraphQL node for Badge model."""

import strawberry
import strawberry_django
from apps.nest.models import Badge


@strawberry_django.type(
    Badge,
    fields=[
        "id",
        "name",
        "description",
        "weight",
        "css_class",
    ],
)
class BadgeNode:
    """GraphQL node for Badge model."""
