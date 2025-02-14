"""OWASP GraphQL queries."""

from .chapter import ChapterQuery
from .committee import CommitteeQuery
from .event import EventQuery
from .project import ProjectQuery


class OwaspQuery(ChapterQuery, CommitteeQuery, EventQuery, ProjectQuery):
    """OWASP queries."""
