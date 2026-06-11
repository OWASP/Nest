"""OWASP app Board Candidate Claim GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


@strawberry_django.type(
    BoardCandidateClaim,
    fields=[
        "created_at",
        "description",
        "is_locked",
        "key",
        "name",
        "status",
        "updated_at",
        "withdrawn_at",
        "withdrawn_reason",
    ],
)
class BoardCandidateClaimNode(strawberry.relay.Node):
    """Board Candidate Claim node."""
