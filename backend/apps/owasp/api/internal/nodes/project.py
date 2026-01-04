"""OWASP project GraphQL node."""

import strawberry
import strawberry_django

from apps.core.utils.index import deep_camelize
from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.repository import RepositoryNode
from apps.owasp.api.internal.nodes.common import GenericEntityNode
from apps.owasp.api.internal.nodes.project_health_metrics import (
    ProjectHealthMetricsNode,
)
from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

RECENT_ISSUES_LIMIT = 5
RECENT_RELEASES_LIMIT = 5
RECENT_PULL_REQUESTS_LIMIT = 5


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
        "open_issues_count",
        "stars_count",
        "summary",
        "type",
    ],
)
class ProjectNode(GenericEntityNode):
    """Project node."""

    @strawberry.field
    def contribution_stats(self) -> strawberry.scalars.JSON | None:
        """Resolve contribution stats with camelCase keys."""
        return deep_camelize(self.contribution_stats)

    @strawberry.field
    def health_metrics_list(self, limit: int = 30) -> list[ProjectHealthMetricsNode]:
        """Resolve project health metrics."""
        return ProjectHealthMetrics.objects.filter(
            project=self,
        ).order_by(
            "nest_created_at",
        )[:limit]

    @strawberry.field
    def health_metrics_latest(self) -> ProjectHealthMetricsNode | None:
        """Resolve latest project health metrics."""
        return (
            ProjectHealthMetrics.get_latest_health_metrics()
            .filter(
                project=self,
            )
            .first()
        )

    @strawberry.field
    def issues_count(self) -> int:
        """Resolve issues count."""
        return self.idx_issues_count

    @strawberry.field
    def key(self) -> str:
        """Resolve key."""
        return self.idx_key

    @strawberry.field
    def languages(self) -> list[str]:
        """Resolve languages."""
        return self.idx_languages

    @strawberry.field
    def recent_issues(self) -> list[IssueNode]:
        """Resolve recent issues."""
        return self.issues.select_related("author").order_by("-created_at")[:RECENT_ISSUES_LIMIT]

    @strawberry.field
    def recent_milestones(self, limit: int = 5) -> list[MilestoneNode]:
        """Resolve recent milestones."""
        return self.recent_milestones.select_related("author").order_by("-created_at")[:limit]

    @strawberry.field
    def recent_pull_requests(self) -> list[PullRequestNode]:
        """Resolve recent pull requests."""
        return self.pull_requests.select_related("author").order_by("-created_at")[
            :RECENT_PULL_REQUESTS_LIMIT
        ]

    @strawberry.field
    def recent_releases(self) -> list[ReleaseNode]:
        """Resolve recent releases."""
        return self.published_releases.order_by("-published_at")[:RECENT_RELEASES_LIMIT]

    @strawberry.field
    def repositories(self) -> list[RepositoryNode]:
        """Resolve repositories."""
        return self.repositories.filter(
            organization__isnull=False,
        ).order_by(
            "-pushed_at",
            "-updated_at",
        )

    @strawberry.field
    def repositories_count(self) -> int:
        """Resolve repositories count."""
        return self.idx_repositories_count

    @strawberry.field
    def topics(self) -> list[str]:
        """Resolve topics."""
        return self.idx_topics
