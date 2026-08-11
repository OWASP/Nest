"""OWASP snapshot subscription GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.models.snapshot_subscription import SnapshotSubscription


@strawberry.type
class SubscribedEntityNode:
    """Subscribed entity node."""

    id: int
    name: str


@strawberry_django.type(
    SnapshotSubscription,
    fields=[
        "name",
        "frequency",
        "include_chapters",
        "include_events",
        "include_issues",
        "include_posts",
        "include_projects",
        "include_pull_requests",
        "include_releases",
        "include_users",
        "is_active",
        "created_at",
        "updated_at",
    ],
)
class SnapshotSubscriptionNode(strawberry.relay.Node):
    """Snapshot subscription node."""

    @strawberry_django.field(prefetch_related=["subscribed_projects"])
    def subscribed_projects(self, root: SnapshotSubscription) -> list[SubscribedEntityNode]:
        """Resolve subscribed projects with id and name."""
        return [SubscribedEntityNode(id=p.pk, name=p.name) for p in root.subscribed_projects.all()]

    @strawberry_django.field(prefetch_related=["subscribed_chapters"])
    def subscribed_chapters(self, root: SnapshotSubscription) -> list[SubscribedEntityNode]:
        """Resolve subscribed chapters with id and name."""
        return [SubscribedEntityNode(id=c.pk, name=c.name) for c in root.subscribed_chapters.all()]

    @strawberry_django.field(prefetch_related=["subscribed_committees"])
    def subscribed_committees(self, root: SnapshotSubscription) -> list[SubscribedEntityNode]:
        """Resolve subscribed committees with id and name."""
        return [
            SubscribedEntityNode(id=c.pk, name=c.name) for c in root.subscribed_committees.all()
        ]
