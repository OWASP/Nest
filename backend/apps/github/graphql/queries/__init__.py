"""GitHub GraphQL queries."""

#!/usr/bin/env python3
from apps.github.graphql.queries.repository import RepositoryQuery
from apps.github.graphql.queries.user import UserQuery


class GithubQuery(RepositoryQuery, UserQuery):
    """GitHub query."""
