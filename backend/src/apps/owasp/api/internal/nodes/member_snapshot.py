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
    def commits_count(self, root: MemberSnapshot) -> int:
        """Resolve commits count."""
        return root.commits_count

    @strawberry_django.field(select_related=["github_user"])
    def github_user(self, root: MemberSnapshot) -> UserNode:
        """Resolve GitHub user."""
        return root.github_user

    @strawberry_django.field
    def issues_count(self, root: MemberSnapshot) -> int:
        """Resolve issues count."""
        return root.issues_count

    @strawberry_django.field
    def pull_requests_count(self, root: MemberSnapshot) -> int:
        """Resolve pull requests count."""
        return root.pull_requests_count

    @strawberry_django.field
    def messages_count(self, root: MemberSnapshot) -> int:
        """Resolve Slack messages count."""
        return root.messages_count

    @strawberry_django.field
    def total_contributions(self, root: MemberSnapshot) -> int:
        """Resolve total contributions."""
        return root.total_contributions
