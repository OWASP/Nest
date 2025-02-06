"""GitHub repository GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.repository import Repository


class RepositoryNode(BaseNode):
    """GitHub repository node."""

    url = graphene.String()
    latest_release = graphene.String()
    owner_key = graphene.String()

    class Meta:
        model = Repository
        fields = (
            "name",
            "forks_count",
            "description",
            "latest_release",
            "license",
            "key",
            "stars_count",
            "open_issues_count",
            "subscribers_count",
            "contributors_count",
        )

    def resolve_url(self, info):
        """Resolve URL."""
        return self.url

    def resolve_latest_release(self, info):
        """Resolve latest release."""
        return self.latest_release

    def resolve_owner_key(self, info):
        """Resolve owner key."""
        return self.owner_key
