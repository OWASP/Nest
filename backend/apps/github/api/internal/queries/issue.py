"""GraphQL queries for handling GitHub issues."""

import strawberry
import strawberry_django
from django.db.models import F, Window
from django.db.models.functions import Rank

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.models.issue import Issue

MAX_LIMIT = 1000


@strawberry.type
class IssueQuery:
    """GraphQL query class for retrieving GitHub issues."""

    @strawberry_django.field(
        select_related=[
            "author",
            "repository",
            "milestone",
            "level",
            "repository",
            "repository__organization",
        ],
        prefetch_related=["labels", "assignees"],
    )
    def recent_issues(
        self,
        *,
        distinct: bool = False,
        limit: int = 5,
        login: str | None = None,
        organization: str | None = None,
    ) -> list[IssueNode]:
        """Resolve recent issues with optional filtering.

        Args:
            distinct (bool): Whether to return unique issues per author and repository.
            limit (int): Maximum number of issues to return.
            login (str, optional): Filter issues by a specific author's login.
            organization (str, optional): Filter issues by a specific organization's login.

        Returns:
            list[IssueNode]: List of issue nodes.

        """
        queryset = Issue.objects.order_by(
            "-created_at",
        )

        filters = {}

        if login:
            filters["author__login"] = login
        if organization:
            filters["repository__organization__login"] = organization

        queryset = queryset.filter(**filters)

        if distinct:
            queryset = (
                queryset.annotate(
                    rank=Window(
                        expression=Rank(),
                        partition_by=[F("author_id")],
                        order_by=F("created_at").desc(),
                    )
                )
                .filter(rank=1)
                .order_by("-created_at")
            )

        return queryset[:limit] if (limit := min(limit, MAX_LIMIT)) > 0 else []
