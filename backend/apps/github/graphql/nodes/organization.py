"""GitHub organization GraphQL node."""

import graphene
from django.db import models

from apps.common.graphql.nodes import BaseNode
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.graphql.nodes.repository import RepositoryNode
from apps.github.graphql.nodes.repository_contributor import RepositoryContributorNode
from apps.github.models.organization import Organization
from apps.github.models.repository import Repository
from apps.github.models.issue import Issue
from apps.github.models.release import Release
from apps.github.models.repository_contributor import RepositoryContributor, TOP_CONTRIBUTORS_LIMIT

RECENT_ISSUES_LIMIT = 6
RECENT_RELEASES_LIMIT = 6
RECENT_REPOSITORIES_LIMIT = 10


class OrganizationStatsNode(graphene.ObjectType):
    """Organization stats node."""

    total_repositories = graphene.Int()
    total_contributors = graphene.Int()
    total_stars = graphene.Int()
    total_forks = graphene.Int()
    total_issues = graphene.Int()


class OrganizationNode(BaseNode):
    """GitHub organization node."""

    url = graphene.String()
    stats = graphene.Field(OrganizationStatsNode)
    repositories = graphene.List(RepositoryNode)
    issues = graphene.List(IssueNode)
    releases = graphene.List(ReleaseNode)
    top_contributors = graphene.List(RepositoryContributorNode)

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

    def resolve_url(self, info):
        """Resolve organization URL."""
        return self.url

    def resolve_stats(self, info):
        """Resolve organization stats."""
        repositories = Repository.objects.filter(organization=self)

        total_repositories = repositories.count()
        total_stars = sum(repo.stars_count for repo in repositories)
        total_forks = sum(repo.forks_count for repo in repositories)
        total_issues = sum(repo.open_issues_count for repo in repositories)

        unique_contributors = RepositoryContributor.objects.filter(
            repository__in=repositories
        ).values('user').distinct().count()

        return OrganizationStatsNode(
            total_repositories=total_repositories,
            total_contributors=unique_contributors,
            total_stars=total_stars,
            total_forks=total_forks,
            total_issues=total_issues,
        )

    def resolve_repositories(self, info):
        """Resolve repositories for the organization."""
        return Repository.objects.filter(organization=self).order_by('-stars_count')[:RECENT_REPOSITORIES_LIMIT]

    def resolve_issues(self, info):
        """Resolve issues for the organization."""
        repositories = Repository.objects.filter(organization=self)
        return Issue.objects.filter(repository__in=repositories).select_related(
            'repository', 'author'
        ).order_by('-created_at')[:RECENT_ISSUES_LIMIT]

    def resolve_releases(self, info):
        """Resolve releases for the organization."""
        repositories = Repository.objects.filter(organization=self)
        return Release.objects.filter(repository__in=repositories).select_related(
            'repository', 'author'
        ).order_by('-published_at')[:RECENT_RELEASES_LIMIT]

    def resolve_top_contributors(self, info):
        """Resolve top contributors for the organization.

        This method gets the top contributors across all repositories in the organization.
        It first groups by user and then orders by contributions count.
        """
        repositories = Repository.objects.filter(organization=self)

        top_contributors = RepositoryContributor.objects.filter(
            repository__in=repositories
        ).values(
            'user__id',
            'user__login',
            'user__name',
            'user__avatar_url',
        ).annotate(
            total_contributions=models.Sum('contributions_count')
        ).order_by('-total_contributions')[:TOP_CONTRIBUTORS_LIMIT]

        return [
            RepositoryContributorNode(
                avatar_url=tc['user__avatar_url'],
                contributions_count=tc['total_contributions'],
                login=tc['user__login'],
                name=tc['user__name'],
            )
            for tc in top_contributors
        ]