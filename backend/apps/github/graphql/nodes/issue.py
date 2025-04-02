"""GitHub issue GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.issue import Issue


class IssueNode(BaseNode):
    """GitHub issue node."""

    url = graphene.String()

    class Meta:
        model = Issue
        fields = (
            "author",
            "comments_count",
            "created_at",
            "state",
            "title",
            "url",
        )

    def resolve_url(self, info):
        """Resolve URL."""
        return self.url
