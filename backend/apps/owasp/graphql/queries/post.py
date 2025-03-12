"""OWASP event GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.post import PostNode
from apps.owasp.models.post import Post


class PostQuery(BaseQuery):
    """GraphQL queries for Post model."""

    recent_posts = graphene.List(PostNode, limit=graphene.Int(default_value=5))

    def resolve_recent_posts(root, info, limit=5):
        """Return the 5 most recent posts."""
        return Post.recent_posts()[:limit]
