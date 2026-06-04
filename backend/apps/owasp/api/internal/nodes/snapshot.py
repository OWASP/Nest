"""OWASP snapshot GraphQL node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.user import UserNode
from apps.owasp.api.internal.nodes.chapter import ChapterNode
from apps.owasp.api.internal.nodes.event import EventNode
from apps.owasp.api.internal.nodes.post import PostNode
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

    chapters: list[ChapterNode] = strawberry_django.field()

    @strawberry_django.field
    def key(self, root: Snapshot) -> str:
        """Resolve key."""
        return root.key

    @strawberry_django.field(prefetch_related=["events"])
    def events(self, root: Snapshot) -> list[EventNode]:
        """Resolve events."""
        return root.events.order_by("-start_date")

    @strawberry_django.field(prefetch_related=["issues"])
    def issues(self, root: Snapshot) -> list[IssueNode]:
        """Resolve issues."""
        return root.issues.order_by("-created_at")[:RECENT_ISSUES_LIMIT]

    @strawberry_django.field(prefetch_related=["posts"])
    def posts(self, root: Snapshot) -> list[PostNode]:
        """Resolve posts."""
        return root.posts.order_by("-published_at")

    @strawberry_django.field(prefetch_related=["projects"])
    def projects(self, root: Snapshot) -> list[ProjectNode]:
        """Resolve projects."""
        return root.projects.order_by("-created_at")

    @strawberry_django.field(prefetch_related=["pull_requests"])
    def pull_requests(self, root: Snapshot) -> list[PullRequestNode]:
        """Resolve pull requests."""
        return root.pull_requests.order_by("-created_at")

    @strawberry_django.field(prefetch_related=["releases"])
    def releases(self, root: Snapshot) -> list[ReleaseNode]:
        """Resolve releases."""
        return root.releases.order_by("-published_at")

    @strawberry_django.field(prefetch_related=["users"])
    def users(self, root: Snapshot) -> list[UserNode]:
        """Resolve users."""
        return root.users.order_by("-created_at")
