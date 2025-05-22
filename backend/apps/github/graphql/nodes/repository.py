"""GitHub repository GraphQL node."""

import strawberry
import strawberry_django

from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.milestone import MilestoneNode
from apps.github.graphql.nodes.organization import OrganizationNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.graphql.nodes.repository_contributor import RepositoryContributorNode
from apps.github.models.repository import Repository

RECENT_ISSUES_LIMIT = 5
RECENT_RELEASES_LIMIT = 5


@strawberry_django.type(
    Repository,
    fields=[
        "commits_count",
        "contributors_count",
        "created_at",
        "description",
        "forks_count",
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
class RepositoryNode:
    """Repository node."""

    @strawberry.field
    def issues(self) -> list[IssueNode]:
        """Resolve recent issues."""
        return self.issues.select_related("author").order_by("-created_at")[:RECENT_ISSUES_LIMIT]

    @strawberry.field
    def languages(self) -> list[str]:
        """Resolve languages."""
        return list(self.languages.keys())

    @strawberry.field
    def latest_release(self) -> str:
        """Resolve latest release."""
        return self.latest_release

    @strawberry.field
    def organization(self) -> OrganizationNode:
        """Resolve organization."""
        return self.organization

    @strawberry.field
    def owner_key(self) -> str:
        """Resolve owner key."""
        return self.owner_key

    @strawberry.field
    def recent_milestones(self, limit: int = 5) -> list[MilestoneNode]:
        """Resolve recent milestones."""
        return self.recent_milestones.select_related("repository").order_by("-created_at")[:limit]

    @strawberry.field
    def releases(self) -> list[ReleaseNode]:
        """Resolve recent releases."""
        return self.published_releases.order_by("-published_at")[:RECENT_RELEASES_LIMIT]

    @strawberry.field
    def top_contributors(self) -> list[RepositoryContributorNode]:
        """Resolve top contributors."""
        return self.idx_top_contributors

    @strawberry.field
    def topics(self) -> list[str]:
        """Resolve topics."""
        return self.topics

    @strawberry.field
    def url(self) -> str:
        """Resolve URL."""
        return self.url
