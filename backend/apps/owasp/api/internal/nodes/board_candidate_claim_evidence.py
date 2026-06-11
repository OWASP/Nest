"""OWASP app Board Candidate Claim Evidence GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence


@strawberry_django.type(
    BoardCandidateClaimEvidence,
    fields=[
        "created_at",
        "description",
        "file_name",
        "file_size",
        "is_removed",
        "key",
        "name",
        "removed_at",
        "removed_reason",
        "source_url",
        "updated_at",
    ],
)
class BoardCandidateClaimEvidenceNode(strawberry.relay.Node):
    """Board Candidate Claim Evidence node."""
