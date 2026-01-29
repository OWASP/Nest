"""OWASP snapshot GraphQL queries."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.snapshot import SnapshotNode
from apps.owasp.models.snapshot import Snapshot

MAX_LIMIT = 10


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

    @strawberry_django.field
    def snapshots(self, limit: int = 12) -> list[SnapshotNode]:
        """Resolve snapshots."""
        if limit <= 0:
            return []

        limit = min(max(limit, 1), MAX_LIMIT)

        return list(
            Snapshot.objects.filter(
                status=Snapshot.Status.COMPLETED,
            )
            .only("id", "key", "title", "created_at")
            .order_by("-created_at")[:limit]
        )
