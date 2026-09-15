"""OWASP snapshot subscription GraphQL queries."""

import strawberry
import strawberry_django
from django.core.exceptions import ValidationError
from strawberry.types import Info

from apps.owasp.api.internal.nodes.snapshot_subscription import SnapshotSubscriptionNode
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


@strawberry.type
class SnapshotSubscriptionQuery:
    """Snapshot subscription queries."""

    @strawberry_django.field
    def my_snapshot_subscriptions(self, info: Info) -> list[SnapshotSubscriptionNode]:
        """Resolve the current user's snapshot subscriptions."""
        user = info.context.request.user
        if not user.is_authenticated:
            return []

        return SnapshotSubscription.objects.filter(user=user).order_by("created_at")

    @strawberry_django.field
    def subscription_by_token(self, token: str) -> SnapshotSubscriptionNode | None:
        """Fetch subscription by unsubscribe token for the filtered snapshot view.

        Args:
            token: The unsubscribe_token UUID string.

        Returns:
            The matching SnapshotSubscriptionNode, or None.

        """
        try:
            return SnapshotSubscription.objects.get(unsubscribe_token=token)
        except (SnapshotSubscription.DoesNotExist, ValidationError, ValueError):
            return None
