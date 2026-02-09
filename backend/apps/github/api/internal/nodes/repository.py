"""GitHub repository GraphQL node."""

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from django.db.models import Prefetch

from apps.common.utils import normalize_limit
from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.api.internal.nodes.organization import OrganizationNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.repository_contributor import RepositoryContributorNode
from apps.github.models.release import Release
from apps.github.models.repository import Repository

if TYPE_CHECKING:
    from apps.owasp.api.internal.nodes.project import ProjectNode

MAX_LIMIT = 1000
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
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        return root.recent_milestones.order_by("-created_at")[:normalized_limit]

    @strawberry_django.field(
        prefetch_related=[
            lambda _: Prefetch(
                "releases",
                queryset=Release.objects.filter(
                    is_draft=False,
                    is_pre_release=False,
                    published_at__isnull=False,
                ).select_related(
                    "author__owasp_profile",
                    "repository__organization",
                ).order_by("-published_at")[:RECENT_RELEASES_LIMIT],
                to_attr="prefetched_releases",
            )
        ]
    )
    def releases(self, root: Repository) -> list[ReleaseNode]:
        """Resolve recent releases."""
        # TODO(arkid15r): rename this to recent_releases.
        return root.prefetched_releases

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
