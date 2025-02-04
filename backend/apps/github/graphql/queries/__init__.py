"""OWASP GraphQL queries."""

from apps.github.graphql.queries.repository import RepositoryQuery


class GithubQuery(RepositoryQuery):
    """OWASP queries."""
