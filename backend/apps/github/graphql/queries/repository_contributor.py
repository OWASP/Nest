"""OWASP repository contributor GraphQL queries."""

import graphene
from django.db.models import F, Window
from django.db.models.functions import Rank

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.repository_contributor import RepositoryContributorNode
from apps.github.models.repository_contributor import RepositoryContributor


class RepositoryContributorQuery(BaseQuery):
    """Repository contributor queries."""

    top_contributors = graphene.List(
        RepositoryContributorNode,
        limit=graphene.Int(default_value=15),
        organization=graphene.String(required=False),
    )

    def resolve_top_contributors(root, info, limit, organization=None):
        """Resolve top contributors only for repositories with projects.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): Maximum number of contributors to return.
            organization (str, optional): Organization login to filter by.

        Returns:
            list: List of top contributors with their details.

        """
        queryset = (
            RepositoryContributor.objects.by_humans()
            .to_community_repositories()
            .filter(repository__project__isnull=False)
            .select_related("user", "repository")
            .annotate(
                rank=Window(
                    expression=Rank(),
                    order_by=F("contributions_count").desc(),
                    partition_by=F("user__login"),
                )
            )
        )

        if organization:
            queryset = queryset.select_related(
                "repository__organization",
            ).filter(
                repository__organization__login=organization,
            )

        top_contributors = (
            queryset.filter(rank=1)
            .annotate(
                project_name=F("repository__project__name"),
                project_url=F("repository__project__key"),
            )
            .values(
                "user__avatar_url",
                "contributions_count",
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
