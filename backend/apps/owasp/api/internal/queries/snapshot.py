"""OWASP snapshot GraphQL queries."""

import strawberry

from apps.owasp.api.internal.nodes.snapshot import SnapshotNode
from apps.owasp.models.snapshot import Snapshot


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
            Snapshot.objects.filter(
                status=Snapshot.Status.COMPLETED,
            ).order_by(
                "-created_at",
            )[:limit]
            if limit > 0
            else []
        )
