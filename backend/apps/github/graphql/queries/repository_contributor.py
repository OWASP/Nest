"""OWASP repository contributor GraphQL queries."""

import graphene
from django.db.models import F, OuterRef, Subquery, Window
from django.db.models.functions import Rank

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.repository_contributor import RepositoryContributorNode
from apps.github.models.repository_contributor import RepositoryContributor
from apps.owasp.models.project import Project


class RepositoryContributorQuery(BaseQuery):
    """Repository contributor queries."""

    top_contributors = graphene.List(
        RepositoryContributorNode, limit=graphene.Int(default_value=15)
    )

    def resolve_top_contributors(root, info, limit):
        """Resolve top contributors only for repositories with projects.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): Maximum number of contributors to return.

        Returns:
            list: List of top contributors with their details.
        """
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
