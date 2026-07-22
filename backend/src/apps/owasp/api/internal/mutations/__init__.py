"""OWASP app mutations."""

import strawberry

from .entity_subscription import EntitySubscriptionMutations
from .snapshot_subscription import SnapshotSubscriptionMutations


@strawberry.type
class OwaspMutations(EntitySubscriptionMutations, SnapshotSubscriptionMutations):
    """OWASP mutations."""
