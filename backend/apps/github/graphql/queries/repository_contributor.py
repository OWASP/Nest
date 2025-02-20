"""OWASP repository contributor GraphQL queries."""

import graphene
from django.db.models import Sum

from apps.common.graphql.queries import BaseQuery
from apps.github.constants import OWASP_FOUNDATION_LOGIN
from apps.github.graphql.nodes.repository_contributor import RepositoryContributorNode
from apps.github.models.organization import Organization
from apps.github.models.repository_contributor import RepositoryContributor


class RepositoryContributorQuery(BaseQuery):
    """Repository contributor queries."""

    top_contributors = graphene.List(
        RepositoryContributorNode, limit=graphene.Int(default_value=15)
    )

    def resolve_top_contributors(root, info, limit):
        """Resolve top contributors."""
        non_indexable_logins = ["ghost", OWASP_FOUNDATION_LOGIN, *list(Organization.get_logins())]

        top_contributors_data = (
            RepositoryContributor.objects.exclude(user__login__in=non_indexable_logins)
            .values("user__avatar_url", "user__login", "user__name")
            .annotate(total_contributions=Sum("contributions_count"))
            .order_by("-total_contributions")[:limit]
        )

        return [
            RepositoryContributorNode(
                avatar_url=contrib["user__avatar_url"],
                contributions_count=contrib["total_contributions"],
                login=contrib["user__login"],
                name=contrib["user__name"],
            )
            for contrib in top_contributors_data
        ]
