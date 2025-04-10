"""GitHub GraphQL queries."""

from apps.github.graphql.queries.issue import IssueQuery
from apps.github.graphql.queries.organization import OrganizationQuery
from apps.github.graphql.queries.pull_request import PullRequestQuery
from apps.github.graphql.queries.release import ReleaseQuery
from apps.github.graphql.queries.repository import RepositoryQuery
from apps.github.graphql.queries.repository_contributor import RepositoryContributorQuery
from apps.github.graphql.queries.user import UserQuery


class GithubQuery(
    IssueQuery,
    OrganizationQuery,
    PullRequestQuery,
    ReleaseQuery,
    RepositoryContributorQuery,
    RepositoryQuery,
    UserQuery,
):
    """GitHub query."""
