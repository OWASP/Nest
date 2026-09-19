"""OWASP activity event GraphQL node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.repository import RepositoryNode
from apps.github.api.internal.nodes.user import UserNode
from apps.owasp.models.activity_event import ActivityEvent


@strawberry_django.type(
    ActivityEvent,
    fields=[
        "activity_type",
        "occurred_at",
    ],
)
class ActivityEventNode(strawberry.relay.Node):
    """Activity event node."""

    @strawberry_django.field(select_related=["github_repository"])
    def github_repository(self, root: ActivityEvent) -> RepositoryNode:
        """Resolve GitHub repository."""
        return root.github_repository

    @strawberry_django.field(select_related=["github_user"])
    def github_user(self, root: ActivityEvent) -> UserNode | None:
        """Resolve GitHub user."""
        return root.github_user

    @strawberry_django.field
    def number(self, root: ActivityEvent) -> int | None:
        """Resolve issue or PR number."""
        return root.source_number

    @strawberry_django.field
    def title(self, root: ActivityEvent) -> str:
        """Resolve title of the source object."""
        return root.source_title

    @strawberry_django.field
    def url(self, root: ActivityEvent) -> str:
        """Resolve URL of the source object."""
        return root.source_url


@strawberry.type
class ActivityEventStatsNode:
    """Statistics summary for activity events node."""

    active_repos: int
    contributors: int
    issues: int
    pull_requests: int
    releases: int
    total_activities: int


@strawberry.type
class PaginatedActivityEvents:
    """A paginated list of activity events."""

    current_page: int
    events: list[ActivityEventNode]
    total_count: int = 0
    total_pages: int
