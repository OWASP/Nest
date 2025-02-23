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
        RepositoryContributorNode, limit=graphene.Int(default_value=15)
    )

    def resolve_top_contributors(root, info, limit):
        """Resolve top contributors."""
        top_repository_contributors = (
            RepositoryContributor.objects.by_humans()
            .to_community_repositories()
            .annotate(
                rank=Window(
                    expression=Rank(),
                    order_by=F("contributions_count").desc(),
                    partition_by=F("user__login"),
                )
            )
            .filter(rank=1)  # Keep only the highest contribution per user
            .values(
                "contributions_count",
                "repository__name",
                "repository__owner__login",
                "user__avatar_url",
                "user__login",
                "user__name",
            )
            .order_by("-contributions_count")[:limit]
        )

        return [
            RepositoryContributorNode(
                avatar_url=trc["user__avatar_url"],
                contributions_count=trc["contributions_count"],
                login=trc["user__login"],
                name=trc["user__name"],
                repository_name=trc["repository__name"],
                repository_url=f"https://github.com/{trc['repository__owner__login']}/{trc['repository__name']}",
            )
            for trc in top_repository_contributors
        ]
