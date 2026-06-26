"""OWASP snapshot subscription GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.models.snapshot_subscription import SnapshotSubscription


@strawberry_django.type(
    SnapshotSubscription,
    fields=[
        "frequency",
        "is_active",
        "include_chapters",
        "include_events",
        "include_issues",
        "include_posts",
        "include_projects",
        "include_pull_requests",
        "include_releases",
        "include_users",
        "created_at",
        "updated_at",
    ],
)
class SnapshotSubscriptionNode(strawberry.relay.Node):
    """Snapshot subscription node."""
