"""OWASP app mutations."""

import strawberry

from .certificate import CertificateMutation
from .snapshot_feedback import SnapshotFeedbackMutations
from .snapshot_subscription import SnapshotSubscriptionMutations


@strawberry.type
class OwaspMutations(SnapshotFeedbackMutations, SnapshotSubscriptionMutations):
    """OWASP GraphQL mutations."""
