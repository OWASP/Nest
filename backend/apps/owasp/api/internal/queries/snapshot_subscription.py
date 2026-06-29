"""OWASP snapshot subscription GraphQL queries."""

import strawberry
import strawberry_django
from strawberry.types import Info

from apps.owasp.api.internal.nodes.snapshot_subscription import SnapshotSubscriptionNode
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


@strawberry.type
class SnapshotSubscriptionQuery:
    """Snapshot subscription queries."""

    @strawberry_django.field
    def my_subscription(self, info: Info) -> SnapshotSubscriptionNode | None:
        """Resolve the current user's snapshot subscription."""
        user = info.context.request.user
        if not user.is_authenticated:
            return None

        try:
            return SnapshotSubscription.objects.get(user=user)
        except SnapshotSubscription.DoesNotExist:
            return None
