"""OWASP GraphQL queries."""

from .chapter import ChapterQuery
from .committee import CommitteeQuery
from .event import EventQuery
from .project import ProjectQuery
from .stats import StatsQuery


class OwaspQuery(ChapterQuery, CommitteeQuery, EventQuery, ProjectQuery, StatsQuery):
    """OWASP queries."""
