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
        "communication_heatmap_data",
        "chapter_contributions",
        "project_contributions",
        "repository_contributions",
        "channel_communications",
    ],
)
class MemberSnapshotNode(strawberry.relay.Node):
    """Member snapshot node."""

    @strawberry_django.field
    def commits_count(self) -> int:
        """Resolve commits count."""
        return self.commits_count

    @strawberry_django.field
    def github_user(self) -> UserNode:
        """Resolve GitHub user."""
        return self.github_user

    @strawberry_django.field
    def issues_count(self) -> int:
        """Resolve issues count."""
        return self.issues_count

    @strawberry_django.field
    def pull_requests_count(self) -> int:
        """Resolve pull requests count."""
        return self.pull_requests_count

    @strawberry_django.field
    def messages_count(self) -> int:
        """Resolve Slack messages count."""
        return self.messages_count

    @strawberry_django.field
    def total_contributions(self) -> int:
        """Resolve total contributions."""
        return self.total_contributions
