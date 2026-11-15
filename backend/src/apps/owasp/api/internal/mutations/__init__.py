"""OWASP app mutations."""

import strawberry

from .snapshot_feedback import SnapshotFeedbackMutations
from .snapshot_subscription import SnapshotSubscriptionMutations


@strawberry.type
class OwaspMutations(SnapshotFeedbackMutations, SnapshotSubscriptionMutations):
    """OWASP mutations."""
