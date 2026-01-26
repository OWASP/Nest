"""OWASP project GraphQL node."""

import strawberry
import strawberry_django

from apps.core.utils.index import deep_camelize
from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.repository import RepositoryNode
from apps.github.models.milestone import Milestone
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
        "open_issues_count",
        "stars_count",
        "summary",
        "type",
    ],
)
class ProjectNode(GenericEntityNode):
    """Project node."""

    @strawberry_django.field
    def contribution_stats(self, root: Project) -> strawberry.scalars.JSON | None:
        """Resolve contribution stats with camelCase keys."""
        return deep_camelize(root.contribution_stats)

    @strawberry_django.field(prefetch_related=["health_metrics"])
    def health_metrics_list(
        self, root: Project, limit: int = 30
    ) -> list[ProjectHealthMetricsNode]:
        """Resolve project health metrics."""
        return (
            root.health_metrics.order_by("nest_created_at")[:limit]
            if (limit := min(limit, MAX_LIMIT)) > 0
            else []
        )

    @strawberry_django.field(prefetch_related=["health_metrics"])
    def health_metrics_latest(self, root: Project) -> ProjectHealthMetricsNode | None:
        """Resolve latest project health metrics."""
        return root.health_metrics.order_by("-nest_created_at").first()

    @strawberry_django.field
    def issues_count(self, root: Project) -> int:
        """Resolve issues count."""
        return root.idx_issues_count

    @strawberry_django.field
    def key(self, root: Project) -> str:
        """Resolve key."""
        return root.idx_key

    @strawberry_django.field
    def languages(self, root: Project) -> list[str]:
        """Resolve languages."""
        return root.idx_languages

    @strawberry_django.field
    def recent_issues(self, root: Project) -> list[IssueNode]:
        """Resolve recent issues."""
        return root.issues.order_by("-created_at")[:RECENT_ISSUES_LIMIT]

    @strawberry_django.field
    def recent_milestones(self, root: Project, limit: int = 5) -> list[MilestoneNode]:
        """Resolve recent milestones."""
        return (
            Milestone.objects.filter(
                repository__in=root.repositories.all(),
            )
            .select_related(
                "repository__organization",
                "author__owasp_profile",
            )
            .prefetch_related(
                "labels",
            )
            .order_by("-created_at")[:limit]
            if (limit := min(limit, MAX_LIMIT)) > 0
            else []
        )

    @strawberry_django.field(
        prefetch_related=[
            "pull_requests__author",
            "pull_requests__milestone",
            "pull_requests__repository__organization",
            "pull_requests__repository",
            "pull_requests__assignees",
            "pull_requests__labels",
        ],
    )
    def recent_pull_requests(self, root: Project) -> list[PullRequestNode]:
        """Resolve recent pull requests."""
        return root.pull_requests.order_by("-created_at")[:RECENT_PULL_REQUESTS_LIMIT]

    @strawberry_django.field
    def recent_releases(self, root: Project) -> list[ReleaseNode]:
        """Resolve recent releases."""
        return root.published_releases.order_by("-published_at")[:RECENT_RELEASES_LIMIT]

    @strawberry_django.field(prefetch_related=["repositories"])
    def repositories(self, root: Project) -> list[RepositoryNode]:
        """Resolve repositories."""
        return root.repositories.filter(
            organization__isnull=False,
        ).order_by(
            "-pushed_at",
            "-updated_at",
        )

    @strawberry_django.field
    def repositories_count(self, root: Project) -> int:
        """Resolve repositories count."""
        return root.idx_repositories_count

    @strawberry_django.field
    def topics(self, root: Project) -> list[str]:
        """Resolve topics."""
        return root.idx_topics
