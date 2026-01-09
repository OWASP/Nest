"""OWASP snapshot GraphQL queries."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.snapshot import SnapshotNode
from apps.owasp.models.snapshot import Snapshot

MAX_LIMIT = 1000


@strawberry.type
class SnapshotQuery:
    """Snapshot queries."""

    @strawberry_django.field
    def snapshot(self, key: str) -> SnapshotNode | None:
        """Resolve snapshot by key."""
        try:
            return Snapshot.objects.get(
                key=key,
                status=Snapshot.Status.COMPLETED,
            )
        except Snapshot.DoesNotExist:
            return None

    @strawberry_django.field(
        prefetch_related=[
            "new_users__badges",
            "new_releases__author__badges",
            "new_chapters__top_contributors",
            "new_projects__top_contributors",
            "new_issues",
        ]
    )
    def snapshots(self, limit: int = 12) -> list[SnapshotNode]:
        """Resolve snapshots."""
        return (
            Snapshot.objects.filter(
                status=Snapshot.Status.COMPLETED,
            ).order_by(
                "-created_at",
            )[:limit]
            if (limit := min(limit, MAX_LIMIT)) > 0
            else []
        )
