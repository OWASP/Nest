"""OWASP blog posts GraphQL nodes."""

import strawberry
import strawberry_django

from apps.owasp.models.post import Post


@strawberry_django.type(
    Post,
    fields=[
        "author_image_url",
        "author_name",
        "published_at",
        "title",
        "url",
    ],
)
class PostNode:
    """Post node."""

    @strawberry.field
    def id(self) -> strawberry.ID:
        """Resolve a unique identifier."""
        return f"PostNode-{self.id}"
