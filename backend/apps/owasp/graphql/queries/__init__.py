"""OWASP GraphQL queries."""

from .chapter import ChapterQuery
from .committee import CommitteeQuery
from .project import ProjectQuery
from .stats import StatsQuery


class OwaspQuery(ChapterQuery, CommitteeQuery, ProjectQuery, StatsQuery):
    """OWASP queries."""
