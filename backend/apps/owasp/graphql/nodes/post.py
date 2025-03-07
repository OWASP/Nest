"""OWASP blog posts GraphQL nodes."""

from apps.common.graphql.nodes import BaseNode
from apps.owasp.models.post import Post


class PostNode(BaseNode):
    """Post node."""

    class Meta:
        model = Post
        fields = (
            "title",
            "date",
            "author",
            "author_image",
            "url",
        )
