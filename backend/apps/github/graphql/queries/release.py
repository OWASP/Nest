"""OWASP release GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.models.release import Release


class ReleaseQuery(BaseQuery):
    """Release queries."""

    recent_releases = graphene.List(
        ReleaseNode,
        limit=graphene.Int(default_value=15),
        distinct=graphene.Boolean(default_value=False),
    )

    def resolve_recent_releases(root, info, limit, distinct):
        """Resolve recent release."""
        query = Release.objects.filter(
            is_draft=False,
            is_pre_release=False,
            published_at__isnull=False,
        ).order_by("-published_at")

        if distinct:
            query = query.distinct("author_id", "project_id")

        return query[:limit]