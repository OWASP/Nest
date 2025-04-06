"""OWASP snapshot GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.snapshot import SnapshotNode
from apps.owasp.models.snapshot import Snapshot


class SnapshotQuery(BaseQuery):
    """Snapshot queries."""

    snapshot = graphene.Field(
        SnapshotNode,
        key=graphene.String(required=True),
    )

    snapshots = graphene.List(
        SnapshotNode,
        limit=graphene.Int(default_value=12),
    )

    def resolve_snapshot(root, info, key):
        """Resolve snapshot by key."""
        try:
            return Snapshot.objects.get(
                key=key,
                status=Snapshot.Status.COMPLETED,
            )
        except Snapshot.DoesNotExist:
            return None

    def resolve_snapshots(root, info, limit):
        """Resolve snapshots."""
        return Snapshot.objects.filter(
            status=Snapshot.Status.COMPLETED,
        ).order_by(
            "-created_at",
        )[:limit]
