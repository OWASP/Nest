"""OWASP event GraphQL queries."""

import strawberry
import strawberry_django

from apps.common.utils import normalize_limit
from apps.owasp.api.internal.nodes.post import PostNode
from apps.owasp.models.post import Post

MAX_LIMIT = 1000


@strawberry.type
class PostQuery:
    """GraphQL queries for Post model."""

    @strawberry_django.field
    def recent_posts(self, limit: int = 5) -> list[PostNode]:
        """Return the most recent posts."""
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []

        return Post.recent_posts()[:normalized_limit]
