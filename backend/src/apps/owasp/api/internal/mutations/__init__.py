"""OWASP app mutations."""

import strawberry

from .certificate import CertificateMutation
from .snapshot_subscription import SnapshotSubscriptionMutations


@strawberry.type
class OwaspMutations(SnapshotSubscriptionMutations):
    """OWASP mutations."""
