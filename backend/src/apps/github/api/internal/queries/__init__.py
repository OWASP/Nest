"""GitHub GraphQL queries."""

from apps.github.api.internal.queries.issue import IssueQuery
from apps.github.api.internal.queries.milestone import MilestoneQuery
from apps.github.api.internal.queries.organization import OrganizationQuery
from apps.github.api.internal.queries.pull_request import PullRequestQuery
from apps.github.api.internal.queries.release import ReleaseQuery
from apps.github.api.internal.queries.repository import RepositoryQuery
from apps.github.api.internal.queries.repository_contributor import RepositoryContributorQuery
from apps.github.api.internal.queries.user import UserQuery


class GithubQuery(
    IssueQuery,
    MilestoneQuery,
    OrganizationQuery,
    PullRequestQuery,
    ReleaseQuery,
    RepositoryContributorQuery,
    RepositoryQuery,
    UserQuery,
):
    """GitHub query."""
