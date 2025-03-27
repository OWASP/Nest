"""OWASP issue GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.models.issue import Issue


class IssueQuery(BaseQuery):
    """Issue queries."""

    recent_issues = graphene.List(
        IssueNode,
        limit=graphene.Int(default_value=6),
        login=graphene.String(required=False),
    )

    def resolve_recent_issues(root, info, limit, login=None):
        """Resolve recent issues."""
        queryset = Issue.objects.select_related("author").order_by("-created_at")
        if login:
            queryset = queryset.filter(author__login=login)

        return queryset[:limit]
