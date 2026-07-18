"""OWASP project GraphQL node."""

import strawberry
import strawberry_django

from apps.common.utils import normalize_limit
from apps.core.utils.index import deep_camelize
from apps.github.api.internal.dataloaders.issue import RECENT_ISSUES_BY_PROJECT_ID
from apps.github.api.internal.dataloaders.milestone import RECENT_MILESTONES_BY_PROJECT_ID
from apps.github.api.internal.dataloaders.pull_request import (
    RECENT_PULL_REQUESTS_BY_PROJECT_ID,
)
from apps.github.api.internal.dataloaders.release import RECENT_RELEASES_BY_PROJECT_ID
from apps.github.api.internal.dataloaders.repository import REPOSITORIES_BY_PROJECT_ID
from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.repository import RepositoryNode
from apps.owasp.api.internal.dataloaders.project import (
    HEALTH_METRICS_LATEST_BY_PROJECT_ID,
    HEALTH_METRICS_LIST_BY_PROJECT_ID,
    ISSUES_COUNT_BY_PROJECT_ID,
    OPEN_ISSUES_COUNT_BY_PROJECT_ID,
    REPOSITORIES_COUNT_BY_PROJECT_ID,
)
from apps.owasp.api.internal.nodes.common import GenericEntityNode
from apps.owasp.api.internal.nodes.project_health_metrics import (
    ProjectHealthMetricsNode,
)
from apps.owasp.models.project import Project

RECENT_ISSUES_LIMIT = 5
RECENT_RELEASES_LIMIT = 5
RECENT_PULL_REQUESTS_LIMIT = 5

MAX_LIMIT = 1000


@strawberry_django.type(
    Project,
    fields=[
        "contribution_data",
        "contributors_count",
        "created_at",
        "forks_count",
        "id",
        "is_active",
        "level",
        "name",
        "stars_count",
        "summary",
        "type",
    ],
)
class ProjectNode(GenericEntityNode):
    """Project node."""

    @strawberry_django.field(only=["contribution_stats"])
    def contribution_stats(self, root: Project) -> strawberry.scalars.JSON | None:
        """Resolve contribution stats with camelCase keys."""
        return deep_camelize(root.contribution_stats)

    @strawberry_django.field
    async def health_metrics_list(
        self, root: Project, info: strawberry.Info, limit: int = 30
    ) -> list[ProjectHealthMetricsNode]:
        """Resolve project health metrics for chart display.

        Returns the N most recent metrics in chronological order (oldest to newest)
        so charts display correctly from left to right.
        """
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        return await info.context.owasp_dataloaders[HEALTH_METRICS_LIST_BY_PROJECT_ID].load(
            (root.pk, normalized_limit)
        )

    @strawberry_django.field
    async def health_metrics_latest(
        self, root: Project, info: strawberry.Info
    ) -> ProjectHealthMetricsNode | None:
        """Resolve latest project health metrics."""
        return await info.context.owasp_dataloaders[HEALTH_METRICS_LATEST_BY_PROJECT_ID].load(
            root.pk
        )

    @strawberry_django.field
    async def issues_count(self, root: Project, info: strawberry.Info) -> int:
        """Resolve issues count."""
        return await info.context.owasp_dataloaders[ISSUES_COUNT_BY_PROJECT_ID].load(root.pk)

    @strawberry_django.field(only=["key"])
    def key(self, root: Project) -> str:
        """Resolve key."""
        return root.idx_key

    @strawberry_django.field(only=["languages"])
    def languages(self, root: Project) -> list[str]:
        """Resolve languages."""
        return root.idx_languages

    @strawberry_django.field
    async def open_issues_count(self, root: Project, info: strawberry.Info) -> int:
        """Resolve open issues count."""
        return await info.context.owasp_dataloaders[OPEN_ISSUES_COUNT_BY_PROJECT_ID].load(root.pk)

    @strawberry_django.field
    async def recent_issues(self, root: Project, info: strawberry.Info) -> list[IssueNode]:
        """Resolve recent issues."""
        return await info.context.github_dataloaders[RECENT_ISSUES_BY_PROJECT_ID].load(
            (root.pk, RECENT_ISSUES_LIMIT)
        )

    @strawberry_django.field
    async def recent_milestones(
        self, root: Project, info: strawberry.Info, limit: int = 5
    ) -> list[MilestoneNode]:
        """Resolve recent milestones."""
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        return await info.context.github_dataloaders[RECENT_MILESTONES_BY_PROJECT_ID].load(
            (root.pk, normalized_limit)
        )

    @strawberry_django.field
    async def recent_pull_requests(
        self, root: Project, info: strawberry.Info
    ) -> list[PullRequestNode]:
        """Resolve recent pull requests."""
        return await info.context.github_dataloaders[RECENT_PULL_REQUESTS_BY_PROJECT_ID].load(
            (root.pk, RECENT_PULL_REQUESTS_LIMIT)
        )

    @strawberry_django.field
    async def recent_releases(self, root: Project, info: strawberry.Info) -> list[ReleaseNode]:
        """Resolve recent releases."""
        return await info.context.github_dataloaders[RECENT_RELEASES_BY_PROJECT_ID].load(
            (root.pk, RECENT_RELEASES_LIMIT)
        )

    @strawberry_django.field
    async def repositories(self, root: Project, info: strawberry.Info) -> list[RepositoryNode]:
        """Resolve repositories."""
        return await info.context.github_dataloaders[REPOSITORIES_BY_PROJECT_ID].load(root.pk)

    @strawberry_django.field
    async def repositories_count(self, root: Project, info: strawberry.Info) -> int:
        """Resolve repositories count."""
        return await info.context.owasp_dataloaders[REPOSITORIES_COUNT_BY_PROJECT_ID].load(root.pk)

    @strawberry_django.field(only=["topics"])
    def topics(self, root: Project) -> list[str]:
        """Resolve topics."""
        return root.idx_topics
