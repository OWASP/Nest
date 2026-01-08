"""OWASP event GraphQL queries."""

import strawberry

from apps.owasp.api.internal.nodes.post import PostNode
from apps.owasp.models.post import Post

MAX_LIMIT = 1000


@strawberry.type
class PostQuery:
    """GraphQL queries for Post model."""

    @strawberry.field
    def recent_posts(self, limit: int = 5) -> list[PostNode]:
        """Return the 5 most recent posts."""
        return Post.recent_posts()[:limit] if (limit := min(limit, MAX_LIMIT)) > 0 else []
