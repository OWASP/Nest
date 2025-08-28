"""GraphQL node for Badge model."""

import strawberry
import strawberry_django

from apps.nest.models.badge import Badge


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
class BadgeNode(strawberry.relay.Node):
    """GraphQL node for Badge model."""
