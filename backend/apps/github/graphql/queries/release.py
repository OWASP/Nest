"""GraphQL queries for handling OWASP releases."""

import graphene
from django.db.models import OuterRef, Subquery

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.release import ReleaseNode
from apps.github.models.release import Release


class ReleaseQuery(BaseQuery):
    """GraphQL query class for retrieving recent GitHub releases."""

    recent_releases = graphene.List(
        ReleaseNode,
        limit=graphene.Int(default_value=6),
        distinct=graphene.Boolean(default_value=False),
        login=graphene.String(required=False),
        organization=graphene.String(required=False),
    )

    def resolve_recent_releases(root, info, limit, distinct=False, login=None, organization=None):
        """Resolve recent releases with optional distinct filtering.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): Maximum number of releases to return.
            distinct (bool): Whether to return unique releases per author and repository.
            login (str): Optional GitHub username for filtering releases.
            organization (str): Optional GitHub organization for filtering releases.

        Returns:
            QuerySet: Queryset containing the filtered list of releases.

        """
        queryset = Release.objects.filter(
            is_draft=False,
            is_pre_release=False,
            published_at__isnull=False,
        ).order_by("-published_at")

        if login:
            queryset = queryset.filter(
                author__login=login,
            )

        if organization:
            queryset = queryset.filter(
                repository__organization__login=organization,
            )

        if distinct:
            latest_release_per_author = (
                queryset.filter(author_id=OuterRef("author_id"))
                .order_by("-published_at")
                .values("id")[:1]
            )
            queryset = queryset.filter(
                id__in=Subquery(latest_release_per_author),
            ).order_by(
                "-published_at",
            )

        return queryset[:limit]
