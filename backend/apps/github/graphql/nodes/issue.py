"""GitHub issue GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.issue import Issue


class IssueNode(BaseNode):
    """GitHub issue node."""

    repository_name = graphene.String()

    class Meta:
        model = Issue
        fields = (
            "author",
            "created_at",
            "state",
            "title",
            "url",
        )

    def resolve_repository_name(self, info):
        """Resolve the repository name."""
        return self.repository.name
