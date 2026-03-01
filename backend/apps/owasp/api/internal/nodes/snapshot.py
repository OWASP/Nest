"""OWASP snapshot GraphQL node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.user import UserNode
from apps.owasp.api.internal.nodes.chapter import ChapterNode
from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.models.snapshot import Snapshot

RECENT_ISSUES_LIMIT = 100


@strawberry_django.type(
    Snapshot,
    fields=[
        "created_at",
        "end_at",
        "start_at",
        "title",
    ],
)
class SnapshotNode(strawberry.relay.Node):
    """Snapshot node."""

    new_chapters: list[ChapterNode] = strawberry_django.field()

    @strawberry_django.field
    def key(self, root: Snapshot) -> str:
        """Resolve key."""
        return root.key

    @strawberry_django.field(prefetch_related=["new_issues"])
    def new_issues(self, root: Snapshot) -> list[IssueNode]:
        """Resolve new issues."""
        return root.new_issues.order_by("-created_at")[:RECENT_ISSUES_LIMIT]

    @strawberry_django.field(prefetch_related=["new_projects"])
    def new_projects(self, root: Snapshot) -> list[ProjectNode]:
        """Resolve new projects."""
        return root.new_projects.order_by("-created_at")

    @strawberry_django.field(prefetch_related=["new_releases"])
    def new_releases(self, root: Snapshot) -> list[ReleaseNode]:
        """Resolve new releases."""
        return root.new_releases.order_by("-published_at")

    @strawberry_django.field(prefetch_related=["new_users"])
    def new_users(self, root: Snapshot) -> list[UserNode]:
        """Resolve new users."""
        return root.new_users.order_by("-created_at")
