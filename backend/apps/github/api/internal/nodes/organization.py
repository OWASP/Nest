"""GitHub organization GraphQL node."""

import strawberry
import strawberry_django
from django.db import models

from apps.github.models.organization import Organization
from apps.github.models.repository import Repository
from apps.github.models.repository_contributor import RepositoryContributor


@strawberry.type
class OrganizationStatsNode:
    """Organization stats node."""

    total_contributors: int
    total_forks: int
    total_issues: int
    total_repositories: int
    total_stars: int


@strawberry_django.type(
    Organization,
    fields=[
        "avatar_url",
        "collaborators_count",
        "company",
        "created_at",
        "description",
        "email",
        "followers_count",
        "location",
        "login",
        "name",
        "updated_at",
    ],
)
class OrganizationNode(strawberry.relay.Node):
    """GitHub organization node."""

    @strawberry.field
    def stats(self) -> OrganizationStatsNode:
        """Resolve organization stats."""
        repositories = Repository.objects.filter(organization=self)

        total_repositories = repositories.count()
        aggregated_stats = repositories.aggregate(
            total_stars=models.Sum("stars_count"),
            total_forks=models.Sum("forks_count"),
            total_issues=models.Sum("open_issues_count"),
        )

        total_stars = aggregated_stats.get("total_stars") or 0
        total_forks = aggregated_stats.get("total_forks") or 0
        total_issues = aggregated_stats.get("total_issues") or 0

        unique_contributors = (
            RepositoryContributor.objects.filter(repository__in=repositories)
            .values("user")
            .distinct()
            .count()
        )

        return OrganizationStatsNode(
            total_repositories=total_repositories,
            total_contributors=unique_contributors,
            total_stars=total_stars,
            total_forks=total_forks,
            total_issues=total_issues,
        )

    @strawberry.field
    def url(self) -> str:
        """Resolve organization URL."""
        return self.url
