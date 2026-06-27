"""OWASP Board Candidate Claim Review GraphQL node."""

from datetime import datetime

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.user import UserNode
from apps.owasp.api.internal.nodes.enum import ReviewDecisionEnum
from apps.owasp.models.board_candidate_claim_review import BoardCandidateClaimReview


@strawberry_django.type(
    BoardCandidateClaimReview,
    fields=[
        "notes",
    ],
)
class BoardCandidateClaimReviewNode(strawberry.relay.Node):
    """Board Candidate Claim Review node."""

    reviewer: UserNode

    @strawberry_django.field
    def created_at(self, root: BoardCandidateClaimReview) -> datetime:
        """Resolve review creation date."""
        return root.nest_created_at

    @strawberry_django.field
    def decision(self, root: BoardCandidateClaimReview) -> ReviewDecisionEnum:
        """Resolve review decision."""
        return ReviewDecisionEnum(root.decision)
