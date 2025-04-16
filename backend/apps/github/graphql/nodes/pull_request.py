"""GitHub Pull Request Node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.pull_request import PullRequest


class PullRequestNode(BaseNode):
    """GitHub pull request node."""

    organization_name = graphene.String()
    repository_name = graphene.String()
    url = graphene.String()

    class Meta:
        model = PullRequest
        fields = (
            "author",
            "created_at",
            "title",
        )

    def resolve_organization_name(self, info):
        """Return organization name."""
        if self.repository.organization:
            return self.repository.organization.login
        return None

    def resolve_repository_name(self, info):
        """Resolve repository name."""
        return self.repository.name

    def resolve_url(self, info):
        """Resolve URL."""
        return self.url
