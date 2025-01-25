"""GitHub issue GraphQL types."""

from apps.common.graphql.nodes import BaseNode
from apps.github.models.issue import Issue


class IssueNode(BaseNode):
    """GitHub issue."""

    class Meta:
        model = Issue
        fields = (
            "author",
            "comments_count",
            "created_at",
            "number",
            "state",
            "title",
        )
