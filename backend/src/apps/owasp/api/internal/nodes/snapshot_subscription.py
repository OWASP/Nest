"""OWASP snapshot subscription GraphQL node."""

import strawberry
import strawberry_django
from strawberry import auto

from apps.owasp.models.snapshot_subscription import SnapshotSubscription


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

    subscribed_projects: auto
    subscribed_chapters: auto
    subscribed_committees: auto
