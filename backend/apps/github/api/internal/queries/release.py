"""GraphQL queries for handling OWASP releases."""

import strawberry
import strawberry_django
from django.db.models import F, Window
from django.db.models.functions import Rank

from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.models.release import Release

MAX_LIMIT = 1000


@strawberry.type
class ReleaseQuery:
    """GraphQL query class for retrieving recent GitHub releases."""

    @strawberry_django.field(select_related=["author", "repository", "repository__organization"])
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
            queryset = queryset.filter(
                author__login=login,
            )

        if organization:
            queryset = queryset.filter(
                repository__organization__login=organization,
            )

        if distinct:
            queryset = (
                queryset.annotate(
                    rank=Window(
                        expression=Rank(),
                        partition_by=[F("author_id")],
                        order_by=F("published_at").desc(),
                    )
                )
                .filter(rank=1)
                .order_by("-published_at")
            )

        return queryset[:limit] if (limit := min(limit, MAX_LIMIT)) > 0 else []
