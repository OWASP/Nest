"""GraphQL node for Badge model."""

import strawberry
import strawberry_django

from apps.nest.models.badge import Badge


@strawberry_django.type(
    Badge,
    fields=[
        "css_class",
        "description",
        "id",
        "name",
        "weight",
    ],
)
class BadgeNode(strawberry.relay.Node):
    """GraphQL node for Badge model."""
