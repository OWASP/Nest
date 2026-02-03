"""GraphQL queries for handling GitHub issues."""

import strawberry
import strawberry_django
from django.db.models import F, Window
from django.db.models.functions import Rank
from django.db.models import Prefetch

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest

MAX_LIMIT = 1000


@strawberry.type
class IssueQuery:
    """GraphQL query class for retrieving GitHub issues."""

    @strawberry_django.field
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
            distinct (bool): Whether to return unique issues per author.
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

        queryset = queryset.prefetch_related(
            Prefetch(
                "pull_requests",
                queryset=PullRequest.objects.only("id", "state", "merged_at"),
                to_attr="prefetched_pull_requests"
            )
        )

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
