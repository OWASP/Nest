"""GraphQL queries for handling GitHub issues."""

import strawberry
from django.db.models import OuterRef, Subquery

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.models.issue import Issue


@strawberry.type
class IssueQuery:
    """GraphQL query class for retrieving GitHub issues."""

    @strawberry.field
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
        queryset = Issue.objects.select_related(
            "author",
            "repository",
            "repository__organization",
        ).order_by(
            "-created_at",
        )

        if login:
            queryset = queryset.filter(
                author__login=login,
            )

        if organization:
            queryset = queryset.filter(
                repository__organization__login=organization,
            )

        if distinct:
            latest_issue_per_author = (
                queryset.filter(author_id=OuterRef("author_id"))
                .order_by("-created_at")
                .values("id")[:1]
            )
            queryset = queryset.filter(
                id__in=Subquery(latest_issue_per_author),
            ).order_by(
                "-created_at",
            )

        return queryset[:limit]
