"""OWASP issue GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.issue import IssueNode
from apps.github.models.issue import Issue


class IssueQuery(BaseQuery):
    """Issue queries."""

    recent_issues = graphene.List(
        IssueNode, 
        limit=graphene.Int(default_value=15), 
        distinct=graphene.Boolean(default_value=False)
    )

    def resolve_recent_issues(root, info, limit=15, distinct=False):
        """Resolve recent issue."""
        query = Issue.objects.order_by("author_id", "repository_id", "-created_at")  

        if distinct:
            query = query.order_by("author_id", "repository_id", "-created_at").distinct("author_id", "repository_id")

        return query[:limit]

