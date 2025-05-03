"""GraphQL queries for handling GitHub issues."""

from __future__ import annotations

import graphene
from django.db.models import OuterRef, QuerySet, Subquery

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.models.issue import Issue


class IssueQuery(BaseQuery):
    """GraphQL query class for retrieving GitHub issues."""

    recent_issues = graphene.List(
        IssueNode,
        distinct=graphene.Boolean(default_value=False),
        limit=graphene.Int(default_value=5),
        login=graphene.String(required=False),
        organization=graphene.String(required=False),
    )

    def resolve_recent_issues(
        root,
        info,
        *,
        distinct: bool = False,
        limit: int = 5,
        login: str | None = None,
        organization: str | None = None,
    ) -> QuerySet:
        """Resolve recent issues with optional filtering.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            distinct (bool): Whether to return unique issues per author and repository.
            limit (int): Maximum number of issues to return.
            login (str, optional): Filter issues by a specific author's login.
            organization (str, optional): Filter issues by a specific organization's login.

        Returns:
            QuerySet: Queryset containing the filtered list of issues.

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
