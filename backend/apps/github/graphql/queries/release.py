"""GraphQL queries for handling OWASP releases."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.models.release import Release


class ReleaseQuery(BaseQuery):
    """GraphQL query class for retrieving recent GitHub releases."""

    recent_releases = graphene.List(
        ReleaseNode,
        limit=graphene.Int(default_value=15),
        distinct=graphene.Boolean(default_value=False),
    )

    def resolve_recent_releases(root, info, limit=15, distinct=False):
        """Resolve recent releases with optional distinct filtering.

        Args:
        ----
            root: The root query object.
            info: The GraphQL execution context.
            limit (int): Maximum number of releases to return.
            distinct (bool): Whether to return unique releases per author and repository.

        Returns:
        -------
            Queryset containing the filtered list of releases.

        """
        query = Release.objects.filter(
            is_draft=False,
            is_pre_release=False,
            published_at__isnull=False,
        ).order_by("author_id", "repository_id", "-published_at")

        if distinct:
            query = query.distinct("author_id", "repository_id")

        return query[:limit]
