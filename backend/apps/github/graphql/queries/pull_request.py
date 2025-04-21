"""Github pull requests GraphQL queries."""

from __future__ import annotations

import graphene
from django.db.models import OuterRef, QuerySet, Subquery

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.pull_request import PullRequestNode
from apps.github.models.pull_request import PullRequest


class PullRequestQuery(BaseQuery):
    """Pull request queries."""

    recent_pull_requests = graphene.List(
        PullRequestNode,
        limit=graphene.Int(default_value=5),
        distinct=graphene.Boolean(default_value=False),
        login=graphene.String(required=False),
        organization=graphene.String(required=False),
    )

    def resolve_recent_pull_requests(
        root,
        info,
        limit: int,
        *,
        distinct: bool = False,
        login: str | None = None,
        organization: str | None = None,
    ) -> QuerySet:
        """Resolve recent pull requests.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            limit (int): Maximum number of pull requests to return.
            distinct (bool): Whether to return unique pull requests per author and repository.
            login (str, optional): Filter pull requests by a specific author's login.
            organization (str, optional): Filter pull requests by a specific organization's login.

        Returns:
            QuerySet: Queryset containing the filtered list of pull requests.

        """
        queryset = PullRequest.objects.select_related(
            "author",
            "repository",
            "repository__organization",
        ).order_by(
            "-created_at",
        )

        if login:
            queryset = queryset.filter(author__login=login)

        if organization:
            queryset = queryset.filter(
                repository__organization__login=organization,
            )

        if distinct:
            latest_pull_request_per_author = (
                queryset.filter(author_id=OuterRef("author_id"))
                .order_by("-created_at")
                .values("id")[:1]
            )
            queryset = queryset.filter(
                id__in=Subquery(latest_pull_request_per_author),
            ).order_by(
                "-created_at",
            )

        return queryset[:limit]
