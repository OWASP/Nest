"""OWASP event GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.post import PostNode
from apps.owasp.models.post import Post



class PostQuery(BaseQuery):
    """GraphQL queries for Post model."""

    recent_posts = graphene.List(PostNode)

    def resolve_recent_posts(root, info):
        """Return the 5 most recent posts."""
        return Post.recent_posts