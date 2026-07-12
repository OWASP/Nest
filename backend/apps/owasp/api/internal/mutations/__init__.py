"""OWASP app mutations."""

import strawberry

from .snapshot_subscription import SnapshotSubscriptionMutations


@strawberry.type
class OwaspMutations(SnapshotSubscriptionMutations):
    """OWASP mutations."""
