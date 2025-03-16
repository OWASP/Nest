"""OWASP snapshot GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.snapshot import SnapshotNode
from apps.owasp.models.snapshot import Snapshot


class SnapshotQuery(BaseQuery):
    """Snapshot queries."""

    all_snapshots = graphene.List(SnapshotNode)

    snapshot = graphene.Field(
        SnapshotNode,
        key=graphene.String(required=True),
    )

    recent_snapshots = graphene.List(
        SnapshotNode,
        limit=graphene.Int(default_value=8),
    )

    def resolve_snapshot(root, info, key):
        """Resolve snapshot by key."""
        try:
            return Snapshot.objects.get(key=key)
        except Snapshot.DoesNotExist:
            return None

    def resolve_recent_snapshots(root, info, limit):
        """Resolve recent snapshots."""
        return Snapshot.objects.order_by("-created_at")[:limit]
