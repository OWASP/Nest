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
from apps.github.models.issue import Issue
from apps.github.models.milestone import Milestone
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

    organization: OrganizationNode | None = strawberry_django.field(
        select_related=["organization"]
    )

    @strawberry_django.field(
        prefetch_related=[
            Prefetch(
                "issues",
                queryset=Issue.objects.order_by("-created_at"),
                to_attr="_recent_issues_prefetched",
            )
        ]
    )
    def issues(self, root: Repository) -> list[IssueNode]:
        """Resolve recent issues."""
        # TODO(arkid15r): rename this to recent_issues.
        prefetched = getattr(root, "_recent_issues_prefetched", None)
        if prefetched is not None:
            return list(prefetched)[:RECENT_ISSUES_LIMIT]

        return list(root.issues.order_by("-created_at"))[:RECENT_ISSUES_LIMIT]

    @strawberry_django.field
    def languages(self, root: Repository) -> list[str]:
        """Resolve languages."""
        return list(root.languages.keys())

    @strawberry_django.field(
        prefetch_related=[
            Prefetch(
                "releases",
                queryset=Release.objects.filter(
                    is_draft=False,
                    is_pre_release=False,
                    published_at__isnull=False,
                ).order_by("-published_at"),
                to_attr="_latest_release_prefetched",
            )
        ]
    )
    def latest_release(self, root: Repository) -> str | None:
        """Resolve latest release."""
        prefetched = getattr(root, "_latest_release_prefetched", None)
        if prefetched:
            return prefetched[0]
        return root.latest_release

    @strawberry_django.field(
        prefetch_related=[Prefetch("project_set", to_attr="_project_prefetched")]
    )
    def project(
        self, root: Repository
    ) -> Annotated["ProjectNode", strawberry.lazy("apps.owasp.api.internal.nodes.project")] | None:
        """Resolve project."""
        prefetched = getattr(root, "_project_prefetched", None)
        if prefetched:
            return prefetched[0]
        return root.project

    @strawberry_django.field(
        prefetch_related=[
            Prefetch(
                "milestones",
                queryset=Milestone.objects.order_by("-created_at"),
                to_attr="_recent_milestones_prefetched",
            )
        ]
    )
    def recent_milestones(self, root: Repository, limit: int = 5) -> list[MilestoneNode]:
        """Resolve recent milestones."""
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        prefetched = getattr(root, "_recent_milestones_prefetched", None)
        if prefetched is not None:
            return list(prefetched)[:normalized_limit]

        return list(root.milestones.order_by("-created_at"))[:normalized_limit]

    @strawberry_django.field(
        prefetch_related=[
            Prefetch(
                "releases",
                queryset=Release.objects.filter(
                    is_draft=False,
                    is_pre_release=False,
                    published_at__isnull=False,
                ).order_by("-published_at"),
                to_attr="_recent_releases_prefetched",
            )
        ]
    )
    def releases(self, root: Repository) -> list[ReleaseNode]:
        """Resolve recent releases."""
        # TODO(arkid15r): rename this to recent_releases.
        prefetched = getattr(root, "_recent_releases_prefetched", None)
        if prefetched is not None:
            return list(prefetched)[:RECENT_RELEASES_LIMIT]

        return list(root.published_releases.order_by("-published_at"))[:RECENT_RELEASES_LIMIT]

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
