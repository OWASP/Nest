"""GitHub Pull Request Node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.pull_request import PullRequest


class PullRequestNode(BaseNode):
    """GitHub pull request node."""

    url = graphene.String()

    class Meta:
        model = PullRequest
        fields = (
            "created_at",
            "title",
        )

    def resolve_url(self, info):
        """Resolve URL."""
        return self.url
