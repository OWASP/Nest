"""OWASP Board Candidate Claim GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


@strawberry_django.type(
    BoardCandidateClaim,
    fields=[
        "description",
        "is_locked",
        "nest_created_at",
        "nest_updated_at",
        "status",
        "title",
        "withdrawn_at",
        "withdrawn_reason",
    ],
)
class BoardCandidateClaimNode(strawberry.relay.Node):
    """Board Candidate Claim node."""
