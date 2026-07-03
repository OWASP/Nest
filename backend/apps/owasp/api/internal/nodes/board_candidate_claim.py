"""OWASP Board Candidate Claim GraphQL node."""

from datetime import datetime

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.board_candidate_claim_review import (
    BoardCandidateClaimReviewNode,
)
from apps.owasp.api.internal.nodes.enum import ClaimStatusEnum
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


@strawberry_django.type(
    BoardCandidateClaim,
    fields=[
        "description",
        "is_locked",
        "key",
        "name",
        "order",
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
    def reviews(
        self, root: BoardCandidateClaim, info: strawberry.Info
    ) -> list[BoardCandidateClaimReviewNode]:
        """Resolve claim reviews."""
        user = info.context.request.user
        is_self = (
            user.is_authenticated
            and user.github_user is not None
            and root.candidate.member is not None
            and user.github_user == root.candidate.member
        )
        is_reviewer = user.is_authenticated and root.board.reviewers.filter(id=user.id).exists()

        if is_self or root.status == BoardCandidateClaim.Status.APPROVED:
            return root.reviews.all()
        if is_reviewer:
            return root.reviews.filter(reviewer=user)
        return []

    @strawberry_django.field
    def status(self, root: BoardCandidateClaim) -> ClaimStatusEnum:
        """Resolve claim status as GraphQL enum."""
        return ClaimStatusEnum(root.status)

    @strawberry_django.field
    def updated_at(self, root: BoardCandidateClaim) -> datetime:
        """Resolve claim last update date."""
        return root.nest_updated_at
