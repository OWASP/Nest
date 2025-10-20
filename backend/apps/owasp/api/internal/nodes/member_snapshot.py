"""OWASP member snapshot GraphQL node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.user import UserNode
from apps.owasp.models.member_snapshot import MemberSnapshot


@strawberry_django.type(
    MemberSnapshot,
    fields=[
        "start_at",
        "end_at",
        "contribution_heatmap_data",
        "chapter_contributions",
        "project_contributions",
    ],
)
class MemberSnapshotNode(strawberry.relay.Node):
    """Member snapshot node."""

    @strawberry.field
    def github_user(self) -> UserNode:
        """Resolve GitHub user."""
        return self.github_user

    @strawberry.field
    def commits_count(self) -> int:
        """Resolve commits count."""
        return self.commits_count

    @strawberry.field
    def pull_requests_count(self) -> int:
        """Resolve pull requests count."""
        return self.pull_requests_count

    @strawberry.field
    def issues_count(self) -> int:
        """Resolve issues count."""
        return self.issues_count

    @strawberry.field
    def total_contributions(self) -> int:
        """Resolve total contributions."""
        return self.total_contributions
