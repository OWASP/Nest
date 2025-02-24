"""OWASP issue GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.models.issue import Issue


class IssueQuery(BaseQuery):
    """Issue queries."""

    recent_issues = graphene.List(IssueNode, limit=graphene.Int(default_value=15))

    def resolve_recent_issues(root, info, limit):
        """Resolve recent issue."""
        return Issue.objects.order_by("-created_at")[:limit]
