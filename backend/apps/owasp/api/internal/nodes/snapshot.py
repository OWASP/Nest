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

    @strawberry.field
    def key(self) -> str:
        """Resolve key."""
        return self.key

    @strawberry_django.field
    def new_chapters(self) -> list[ChapterNode]:
        """Resolve new chapters."""
        return self.new_chapters.all()

    @strawberry_django.field
    def new_issues(self) -> list[IssueNode]:
        """Resolve new issues."""
        return self.new_issues.order_by("-created_at")[:RECENT_ISSUES_LIMIT]

    @strawberry_django.field
    def new_projects(self) -> list[ProjectNode]:
        """Resolve new projects."""
        return self.new_projects.order_by("-created_at")

    @strawberry_django.field
    def new_releases(self) -> list[ReleaseNode]:
        """Resolve new releases."""
        return self.new_releases.order_by("-published_at")

    @strawberry_django.field
    def new_users(self) -> list[UserNode]:
        """Resolve new users."""
        return self.new_users.order_by("-created_at")
