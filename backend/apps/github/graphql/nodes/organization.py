"""GitHub organization GraphQL node."""

import graphene
from django.db import models

from apps.common.graphql.nodes import BaseNode
from apps.github.models.organization import Organization
from apps.github.models.repository import Repository
from apps.github.models.repository_contributor import RepositoryContributor


class OrganizationStatsNode(graphene.ObjectType):
    """Organization stats node."""

    total_repositories = graphene.Int()
    total_contributors = graphene.Int()
    total_stars = graphene.Int()
    total_forks = graphene.Int()
    total_issues = graphene.Int()


class OrganizationNode(BaseNode):
    """GitHub organization node."""

    stats = graphene.Field(OrganizationStatsNode)
    url = graphene.String()

    class Meta:
        model = Organization
        fields = (
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
        )

    def resolve_stats(self, info):
        """Resolve organization stats."""
        repositories = Repository.objects.filter(organization=self)

        total_repositories = repositories.count()
        aggregated_stats = repositories.aggregate(
            total_stars=models.Sum("stars_count"),
            total_forks=models.Sum("forks_count"),
            total_issues=models.Sum("open_issues_count"),
        )
        total_stars = aggregated_stats["total_stars"] or 0
        total_forks = aggregated_stats["total_forks"] or 0
        total_issues = aggregated_stats["total_issues"] or 0

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

    def resolve_url(self, info):
        """Resolve organization URL."""
        return self.url
