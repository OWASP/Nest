"""OWASP entity subscription GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.entity_subscription_preference import (
    EntitySubscriptionPreferenceNode,
)
from apps.owasp.models.entity_subscription import EntitySubscription


@strawberry_django.type(
    EntitySubscription,
    fields=[
        "frequency",
        "is_active",
        "name",
        "created_at",
        "updated_at",
    ],
)
class EntitySubscriptionNode(strawberry.relay.Node):
    """Entity subscription node."""

    @strawberry_django.field(
        prefetch_related=[
            "entity_preferences__chapter",
            "entity_preferences__committee",
            "entity_preferences__project",
        ],
    )
    def entity_preferences(
        self, root: EntitySubscription
    ) -> list[EntitySubscriptionPreferenceNode]:
        """Resolve entity subscription preferences."""
        return root.entity_preferences.all()
