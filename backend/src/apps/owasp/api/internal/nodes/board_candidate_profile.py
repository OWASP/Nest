"""OWASP Board Candidate Profile GraphQL node."""

from datetime import datetime

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.entity_member import EntityMemberNode
from apps.owasp.models.board_candidate_profile import BoardCandidateProfile


@strawberry_django.type(
    BoardCandidateProfile,
    fields=[
        "raw_markdown",
    ],
)
class BoardCandidateProfileNode(strawberry.relay.Node):
    """Board Candidate Profile node."""

    @strawberry_django.field
    def candidate(self, root: BoardCandidateProfile) -> EntityMemberNode:
        """Resolve candidate."""
        return root.candidate

    @strawberry_django.field
    def created_at(self, root: BoardCandidateProfile) -> datetime:
        """Resolve profile creation date."""
        return root.nest_created_at

    @strawberry_django.field
    def updated_at(self, root: BoardCandidateProfile) -> datetime:
        """Resolve profile last update date."""
        return root.nest_updated_at
