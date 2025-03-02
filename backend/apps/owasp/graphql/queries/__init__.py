"""OWASP GraphQL queries."""

from .chapter import ChapterQuery
from .committee import CommitteeQuery
from .project import ProjectQuery
from .snapshot import SnapshotQuery
from .stats import StatsQuery


class OwaspQuery(ChapterQuery, CommitteeQuery, ProjectQuery, SnapshotQuery, StatsQuery):
    """OWASP queries."""
