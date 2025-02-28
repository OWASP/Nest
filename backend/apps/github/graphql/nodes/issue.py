"""GitHub issue GraphQL node."""

from apps.common.graphql.nodes import BaseNode
from apps.github.models.issue import Issue


class IssueNode(BaseNode):
    """GitHub issue node."""

    class Meta:
        model = Issue
        fields = (
            "author",
            "comments_count",
            "created_at",
            "url",
            "number",
            "state",
            "title",
        )
