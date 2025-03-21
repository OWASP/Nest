"""OWASP repository contributor GraphQL queries."""

import graphene
from django.db.models import F, OuterRef, Subquery, Window
from django.db.models.functions import Rank

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.repository import RepositoryNode
from apps.github.graphql.nodes.repository_contributor import RepositoryContributorNode
from apps.github.models.repository import Repository
from apps.github.models.repository_contributor import RepositoryContributor
from apps.owasp.models.project import Project


class RepositoryContributorQuery(BaseQuery):
    """Repository contributor queries."""

    top_contributors = graphene.List(
        RepositoryContributorNode, limit=graphene.Int(default_value=15)
    )

    top_repositories = graphene.List(RepositoryNode, login=graphene.String(required=True))

    def resolve_top_contributors(root, info, limit):
        """Resolve top contributors only for repositories with projects."""
        top_contributors = (
            RepositoryContributor.objects.by_humans()
            .to_community_repositories()
            .filter(repository__project__isnull=False)  # Repositories with projects
            .annotate(
                project_id=Subquery(
                    Project.repositories.through.objects.filter(
                        repository=OuterRef("repository_id")
                    )
                    .values("project_id")
                    .order_by("project_id")[:1]  # Select the first project ID per repository
                ),
                project_name=Subquery(
                    Project.objects.filter(id=OuterRef("project_id")).values("name")[:1]
                ),
                project_url=Subquery(
                    Project.objects.filter(id=OuterRef("project_id")).values("key")[:1]
                ),
                rank=Window(
                    expression=Rank(),
                    order_by=F("contributions_count").desc(),
                    partition_by=F("user__login"),
                ),
            )
            .filter(rank=1)  # Keep only the highest contribution per user
            .values(
                "contributions_count",
                "user__avatar_url",
                "user__login",
                "user__name",
                "project_name",
                "project_url",
            )
            .order_by("-contributions_count")[:limit]
        )

        return [
            RepositoryContributorNode(
                avatar_url=trc["user__avatar_url"],
                contributions_count=trc["contributions_count"],
                login=trc["user__login"],
                name=trc["user__name"],
                project_name=trc["project_name"],
                project_url=trc["project_url"],
            )
            for trc in top_contributors
        ]

    def resolve_top_repositories(root, info, login):
        """Resolve top repositories for a specific user based on contribution count."""
        top_repo_ids = (
            RepositoryContributor.objects.filter(user__login=login)
            .values_list("repository_id", flat=True)
            .order_by("-contributions_count")
        )

        if not top_repo_ids:
            return []

        repositories = Repository.objects.filter(id__in=top_repo_ids)

        contribution_map = {
            rc.repository_id: rc.contributions_count
            for rc in RepositoryContributor.objects.filter(
                user__login=login, repository_id__in=top_repo_ids
            )
        }

        # Sort repositories by contribution count
        sorted_repositories = sorted(
            repositories, key=lambda repo: contribution_map.get(repo.id, 0), reverse=True
        )
        return [
            RepositoryNode(
                commits_count=repo.commits_count,
                contributors_count=repo.contributors_count,
                created_at=repo.created_at,
                description=repo.description,
                forks_count=repo.forks_count,
                key=repo.key,
                languages=repo.languages,
                license=repo.license,
                name=repo.name,
                open_issues_count=repo.open_issues_count,
                size=repo.size,
                stars_count=repo.stars_count,
                subscribers_count=repo.subscribers_count,
                topics=repo.topics,
                updated_at=repo.updated_at,
                url=repo.url,
            )
            for repo in sorted_repositories
        ]
