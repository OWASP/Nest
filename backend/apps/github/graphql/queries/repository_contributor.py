"""OWASP repository contributor GraphQL queries."""

from __future__ import annotations

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
        excludedUsernames=graphene.List(graphene.String, required=False),
    )

    def resolve_top_contributors(
        root,
        info,
        *,
        limit: int = 15,
        organization: str | None = None,
        excluded_usernames=None,
        project_key: str | None = None,
    ) -> list[RepositoryContributorNode]:
        """Resolve top contributors only for repositories with projects.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): Maximum number of contributors to return.
            organization (str, optional): Organization login to filter by.
            excluded_usernames (list, optional): List of usernames to exclude from the results.
            project_key (str, optional): Project key to filter contributors.

        Returns:
            list: List of top contributors with their details.

        """
        queryset = (
            RepositoryContributor.objects.by_humans()
            .to_community_repositories()
            .filter(repository__project__isnull=False)
            .select_related("repository__project", "user")
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

        if excluded_usernames:
            queryset = queryset.exclude(user__login__in=excluded_usernames)

        if project_key:
            queryset = queryset.filter(repository__project__key=project_key)

        top_contributors = (
            queryset.filter(rank=1)
            .annotate(
                project_name=F("repository__project__name"),
                project_key=F("repository__project__key"),
            )
            .values(
                "contributions_count",
                "user__avatar_url",
                "user__login",
                "user__name",
                "project_key",
                "project_name",
            )
            .order_by("-contributions_count")[:limit]
        )

        return [
            RepositoryContributorNode(
                avatar_url=trc["user__avatar_url"],
                contributions_count=trc["contributions_count"],
                login=trc["user__login"],
                name=trc["user__name"],
                project_key=trc["project_key"].replace("www-project-", ""),
                project_name=trc["project_name"],
            )
            for trc in top_contributors
        ]
