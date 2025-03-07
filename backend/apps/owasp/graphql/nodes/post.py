"""OWASP blog posts GraphQL nodes."""

from apps.owasp.models.post import Post
from apps.common.graphql.nodes import BaseNode


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