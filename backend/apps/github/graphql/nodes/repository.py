"""GitHub repository GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.repository import Repository


class RepositoryNode(BaseNode):
    """GitHub repository node."""

    url = graphene.String()

    class Meta:
        model = Repository
        fields = (
            "name",
            "forks_count",
            "stars_count",
            "open_issues_count",
            "subscribers_count",
            "contributors_count",
        )

    def resolve_url(self, info):
        """Resolve URL."""
        return self.url
