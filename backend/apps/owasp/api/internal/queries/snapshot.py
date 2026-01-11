"""OWASP snapshot GraphQL queries."""

import strawberry_django

from apps.owasp.api.internal.nodes.snapshot import SnapshotNode
from apps.owasp.models.snapshot import Snapshot

MAX_LIMIT = 100


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
            "new_users__user_badges__badge",
            "new_projects__owasp_repository",
            "new_chapters__owasp_repository",
            "new_issues__repository",
            "new_issues__labels",
            "new_releases__author__user_badges__badge",
            "new_releases__repository",
        ],
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
