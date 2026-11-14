"""OWASP snapshot GraphQL queries."""

import contextlib
from datetime import datetime

import strawberry
import strawberry_django

from apps.common.utils import normalize_limit
from apps.owasp.api.internal.nodes.snapshot import SnapshotNode
from apps.owasp.models.snapshot import Snapshot

MAX_LIMIT = 100


def _filtered_snapshots(start_at_gte=None, start_at_lte=None):
    """Return a filtered queryset of completed snapshots."""
    queryset = Snapshot.objects.filter(
        status=Snapshot.Status.COMPLETED,
    ).order_by("-created_at")

    if start_at_gte:
        with contextlib.suppress(ValueError):
            queryset = queryset.filter(start_at__gte=datetime.fromisoformat(start_at_gte))
    if start_at_lte:
        with contextlib.suppress(ValueError):
            queryset = queryset.filter(start_at__lte=datetime.fromisoformat(start_at_lte))

    return queryset


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
    def snapshots(
        self,
        limit: int = 12,
        offset: int = 0,
        start_at_gte: str | None = None,
        start_at_lte: str | None = None,
    ) -> list[SnapshotNode]:
        """Resolve snapshots."""
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        normalized_offset = max(0, offset)
        queryset = _filtered_snapshots(start_at_gte, start_at_lte)
        return list(queryset[normalized_offset : normalized_offset + normalized_limit])

    @strawberry_django.field
    def snapshots_count(
        self,
        start_at_gte: str | None = None,
        start_at_lte: str | None = None,
    ) -> int:
        """Resolve total count of snapshots for pagination."""
        return _filtered_snapshots(start_at_gte, start_at_lte).count()
