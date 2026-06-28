"""GitHub repository GraphQL node."""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.types import Info

from apps.common.utils import normalize_limit
from apps.github.api.internal.dataloaders.issue import ISSUES_BY_REPOSITORY_ID_LOADER
from apps.github.api.internal.dataloaders.release import (
    LATEST_RELEASE_BY_REPOSITORY_ID_LOADER,
    RECENT_RELEASES_BY_REPOSITORY_ID_LOADER,
)
from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.api.internal.nodes.organization import OrganizationNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.repository_contributor import RepositoryContributorNode
from apps.github.models.repository import Repository

if TYPE_CHECKING:
    from apps.owasp.api.internal.nodes.project import ProjectNode

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

    @strawberry_django.field
    async def issues(self, root: Repository, info: Info) -> list[IssueNode]:
        """Resolve recent issues."""
        # TODO(arkid15r): rename this to recent_issues.
        return await info.context.github_dataloaders[ISSUES_BY_REPOSITORY_ID_LOADER].load(root.pk)

    @strawberry_django.field(only=["languages"])
    def languages(self, root: Repository) -> list[str]:
        """Resolve languages."""
        return list(root.languages.keys())

    @strawberry_django.field
    async def latest_release(self, root: Repository, info: Info) -> ReleaseNode | None:
        """Resolve latest release."""
        return await info.context.github_dataloaders[LATEST_RELEASE_BY_REPOSITORY_ID_LOADER].load(
            root.pk
        )

    @strawberry_django.field(prefetch_related=["project_set"])
    def project(
        self, root: Repository
    ) -> Annotated["ProjectNode", strawberry.lazy("apps.owasp.api.internal.nodes.project")] | None:
        """Resolve project."""
        return root.project

    @strawberry_django.field(prefetch_related=["milestones"])
    def recent_milestones(self, root: Repository, limit: int = 5) -> list[MilestoneNode]:
        """Resolve recent milestones."""
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        return root.recent_milestones.order_by("-created_at")[:normalized_limit]

    @strawberry_django.field
    async def releases(self, root: Repository, info: Info) -> list[ReleaseNode]:
        """Resolve recent releases."""
        # TODO(arkid15r): rename this to recent_releases.
        return await info.context.github_dataloaders[RECENT_RELEASES_BY_REPOSITORY_ID_LOADER].load(
            root.pk
        )

    @strawberry_django.field
    def top_contributors(self, root: Repository) -> list[RepositoryContributorNode]:
        """Resolve top contributors."""
        return [RepositoryContributorNode(**tc) for tc in root.idx_top_contributors]

    @strawberry_django.field(only=["topics"])
    def topics(self, root: Repository) -> list[str]:
        """Resolve topics."""
        return root.topics

    @strawberry_django.field(select_related=["owner"], only=["owner__login", "name"])
    def url(self, root: Repository) -> str:
        """Resolve URL."""
        return root.url
