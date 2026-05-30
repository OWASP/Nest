"""OWASP Board Candidate Claim Evidence GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence


@strawberry_django.type(
    BoardCandidateClaimEvidence,
    fields=[
        "description",
        "file_name",
        "file_size",
        "is_removed",
        "nest_created_at",
        "nest_updated_at",
        "removed_at",
        "removed_reason",
        "source_url",
        "title",
    ],
)
class BoardCandidateClaimEvidenceNode(strawberry.relay.Node):
    """Board Candidate Claim Evidence node."""

    @strawberry_django.field
    def file_url(self) -> str | None:
        """Return a URL to access the evidence file."""
        if not self.file:
            return None
        return self.file.url
