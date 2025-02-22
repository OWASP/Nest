"""OWASP release GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.models.release import Release


class ReleaseQuery(BaseQuery):
    """Release queries."""

    recent_releases = graphene.List(ReleaseNode, limit=graphene.Int(default_value=15))

    def resolve_recent_releases(root, info, limit):
        """Resolve recent release."""
        return Release.objects.order_by("-created_at")[:limit]
