"""GraphQL queries for handling OWASP releases."""

import strawberry
from django.db.models import OuterRef, Subquery

from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.models.release import Release


@strawberry.type
class ReleaseQuery:
    """GraphQL query class for retrieving recent GitHub releases."""

    @strawberry.field
    def recent_releases(
        self,
        *,
        distinct: bool = False,
        limit: int = 6,
        login: str | None = None,
        organization: str | None = None,
    ) -> list[ReleaseNode]:
        """Resolve recent releases with optional distinct filtering.

        Args:
            distinct (bool): Whether to return unique releases per author and repository.
            limit (int): Maximum number of releases to return.
            login (str, optional): Filter releases by a specific author's login.
            organization (str, optional): Filter releases by a specific organization's login.

        Returns:
            list[ReleaseNode]: List of release nodes containing the filtered list of releases.

        """
        queryset = Release.objects.filter(
            is_draft=False,
            is_pre_release=False,
            published_at__isnull=False,
        ).order_by("-published_at")

        if login:
            queryset = queryset.select_related(
                "author",
                "repository",
                "repository__organization",
            ).filter(
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

        return queryset[:limit] if limit > 0 else []
