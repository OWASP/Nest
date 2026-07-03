"""OWASP snapshot subscription GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.chapter import ChapterNode
from apps.owasp.api.internal.nodes.project_subscription_preference import (
    ProjectSubscriptionPreferenceNode,
)
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


@strawberry_django.type(
    SnapshotSubscription,
    fields=[
        "frequency",
        "is_active",
        "include_chapters",
        "include_events",
        "include_posts",
        "include_users",
        "created_at",
        "updated_at",
    ],
)
class SnapshotSubscriptionNode(strawberry.relay.Node):
    """Snapshot subscription node."""

    @strawberry_django.field(prefetch_related=["project_preferences__project"])
    def project_preferences(
        self, root: SnapshotSubscription
    ) -> list[ProjectSubscriptionPreferenceNode]:
        """Resolve per-project subscription preferences."""
        return root.project_preferences.all()

    @strawberry_django.field(prefetch_related=["chapters"])
    def chapters(self, root: SnapshotSubscription) -> list[ChapterNode]:
        """Resolve subscribed chapters."""
        return root.chapters.all()
