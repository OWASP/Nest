"""OWASP Board Candidate Claim GraphQL node."""

from datetime import datetime

import strawberry
import strawberry_django

from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


@strawberry_django.type(
    BoardCandidateClaim,
    fields=[
        "description",
        "is_locked",
        "order",
        "status",
        "title",
        "withdrawn_at",
        "withdrawn_reason",
    ],
)
class BoardCandidateClaimNode(strawberry.relay.Node):
    """Board Candidate Claim node."""

    @strawberry_django.field
    def created_at(self, root: BoardCandidateClaim) -> datetime:
        """Resolve claim creation date."""
        return root.nest_created_at

    @strawberry_django.field
    def updated_at(self, root: BoardCandidateClaim) -> datetime:
        """Resolve claim last update date."""
        return root.nest_updated_at
