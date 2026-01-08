"""OWASP snapshot GraphQL queries."""

import strawberry

from apps.owasp.api.internal.nodes.snapshot import SnapshotNode
from apps.owasp.models.snapshot import Snapshot

MAX_LIMIT = 1000


@strawberry.type
class SnapshotQuery:
    """Snapshot queries."""

    @strawberry.field
    def snapshot(self, key: str) -> SnapshotNode | None:
        """Resolve snapshot by key."""
        try:
            return Snapshot.objects.get(
                key=key,
                status=Snapshot.Status.COMPLETED,
            )
        except Snapshot.DoesNotExist:
            return None

    @strawberry.field
    def snapshots(self, limit: int = 12) -> list[SnapshotNode]:
        """Resolve snapshots."""
        return (
            Snapshot.objects.prefetch_related(
                "new_chapters", "new_issues", "new_projects", "new_releases", "new_users"
            )
            .filter(
                status=Snapshot.Status.COMPLETED,
            )
            .order_by(
                "-created_at",
            )[:limit]
            if (limit := min(limit, MAX_LIMIT)) > 0
            else []
        )
