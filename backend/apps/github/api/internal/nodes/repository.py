"""GitHub repository GraphQL node."""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.api.internal.nodes.organization import OrganizationNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.repository_contributor import RepositoryContributorNode
from apps.github.models.repository import Repository

if TYPE_CHECKING:
    from apps.owasp.api.internal.nodes.project import ProjectNode

RECENT_ISSUES_LIMIT = 5
RECENT_RELEASES_LIMIT = 5
MAX_LIMIT = 1000


@strawberry_django.type(
    Repository,
    fields=[
        "commits_count",
        "contributors_count",
        "created_at",
        "description",
        "forks_count",
        "is_archived",
        "key",
        "license",
        "name",
        "open_issues_count",
        "size",
        "stars_count",
        "subscribers_count",
        "updated_at",
    ],
)
class RepositoryNode(strawberry.relay.Node):
    """Repository node."""

    organization: OrganizationNode | None = strawberry_django.field()

    @strawberry_django.field(prefetch_related=["issues"])
    def issues(self, root: Repository) -> list[IssueNode]:
        """Resolve recent issues."""
        # TODO(arkid15r): rename this to recent_issues.
        return root.issues.order_by("-created_at")[:RECENT_ISSUES_LIMIT]

    @strawberry_django.field
    def languages(self, root: Repository) -> list[str]:
        """Resolve languages."""
        return list(root.languages.keys())

    @strawberry_django.field
    def latest_release(self, root: Repository) -> str | None:
        """Resolve latest release."""
        return root.latest_release

    @strawberry_django.field(prefetch_related=["project_set"])
    def project(
        self, root: Repository
    ) -> Annotated["ProjectNode", strawberry.lazy("apps.owasp.api.internal.nodes.project")] | None:
        """Resolve project."""
        return root.project

    @strawberry_django.field(prefetch_related=["milestones"])
    def recent_milestones(self, root: Repository, limit: int = 5) -> list[MilestoneNode]:
        """Resolve recent milestones."""
        if limit <= 0:
            return []
        limit = min(limit, MAX_LIMIT)
        return root.recent_milestones.order_by("-created_at")[:limit]

    @strawberry_django.field(prefetch_related=["releases"])
    def releases(self, root: Repository) -> list[ReleaseNode]:
        """Resolve recent releases."""
        # TODO(arkid15r): rename this to recent_releases.
        return root.published_releases.order_by("-published_at")[:RECENT_RELEASES_LIMIT]

    @strawberry_django.field
    def top_contributors(self, root: Repository) -> list[RepositoryContributorNode]:
        """Resolve top contributors."""
        return [RepositoryContributorNode(**tc) for tc in root.idx_top_contributors]

    @strawberry_django.field
    def topics(self, root: Repository) -> list[str]:
        """Resolve topics."""
        return root.topics

    @strawberry_django.field
    def url(self, root: Repository) -> str:
        """Resolve URL."""
        return root.url
