"""Github pull requests GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.pull_request import PullRequestNode
from apps.github.models.pull_request import PullRequest


class PullRequestQuery(BaseQuery):
    """Pull request queries."""

    pull_requests = graphene.List(
        PullRequestNode, limit=graphene.Int(default_value=15), login=graphene.String()
    )

    def resolve_pull_requests(root, info, limit, login):
        """Resolve recent pull requests."""
        return PullRequest.objects.filter(author__login=login)[:limit]
