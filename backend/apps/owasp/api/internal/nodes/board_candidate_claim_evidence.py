"""OWASP Board Candidate Claim Evidence GraphQL node."""

from datetime import datetime

import strawberry
import strawberry_django

from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence


@strawberry_django.type(
    BoardCandidateClaimEvidence,
    fields=[
        "description",
        "key",
        "name",
        "source_url",
    ],
)
class BoardCandidateClaimEvidenceNode(strawberry.relay.Node):
    """Board Candidate Claim Evidence node."""

    @strawberry_django.field
    def created_at(self, root: BoardCandidateClaimEvidence) -> datetime:
        """Resolve evidence creation date."""
        return root.nest_created_at

    @strawberry_django.field
    def has_file(self, root: BoardCandidateClaimEvidence) -> bool:
        """Resolve whether evidence has a file."""
        return bool(root.file)

    @strawberry_django.field
    def updated_at(self, root: BoardCandidateClaimEvidence) -> datetime:
        """Resolve evidence last update date."""
        return root.nest_updated_at
