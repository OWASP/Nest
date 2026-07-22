"""OWASP entity subscription GraphQL queries."""

import strawberry
import strawberry_django
from strawberry.types import Info

from apps.owasp.api.internal.nodes.entity_subscription import EntitySubscriptionNode
from apps.owasp.models.entity_subscription import EntitySubscription


@strawberry.type
class EntitySubscriptionQuery:
    """Entity subscription queries."""

    @strawberry_django.field
    def my_entity_subscriptions(self, info: Info) -> list[EntitySubscriptionNode]:
        """Resolve the current user's entity subscriptions."""
        user = info.context.request.user
        if not user.is_authenticated:
            return []

        return EntitySubscription.objects.filter(user=user)
