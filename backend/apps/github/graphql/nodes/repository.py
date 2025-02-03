"""GitHub repository GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.repository import Repository


class RepositoryNode(BaseNode):
    """GitHub repository node."""

    repository_url = graphene.String()

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

    def resolve_repository_url(self, info):
        """Resolve all URLs."""
        return self.repository_url
