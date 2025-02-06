"""OWASP GraphQL queries."""

from apps.owasp.graphql.queries.chapter import ChapterQuery
from apps.owasp.graphql.queries.project import ProjectQuery


class OwaspQuery(ProjectQuery, ChapterQuery):
    """OWASP queries."""
