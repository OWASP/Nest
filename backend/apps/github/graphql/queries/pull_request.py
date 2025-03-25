"""Github pull requests GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.pull_request import PullRequestNode
from apps.github.models.pull_request import PullRequest


class PullRequestQuery(BaseQuery):
    """Pull request queries."""

    recent_pull_requests = graphene.List(
        PullRequestNode,
        limit=graphene.Int(default_value=6),
        login=graphene.String(required=False),
    )

    def resolve_recent_pull_requests(root, info, limit, login=None):
        """Resolve recent pull requests."""
        queryset = PullRequest.objects.select_related("author").order_by("-created_at")
        if login:
            queryset = queryset.filter(author__login=login)

        return queryset[:limit]
