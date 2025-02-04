"""OWASP GraphQL queries."""

from apps.owasp.graphql.queries.event import EventQuery
from apps.owasp.graphql.queries.project import ProjectQuery


class OwaspQuery(ProjectQuery, EventQuery):
    """OWASP queries."""
