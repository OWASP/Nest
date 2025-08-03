"""OWASP GraphQL queries."""

from .chapter import ChapterQuery
from .committee import CommitteeQuery
from .event import EventQuery
from .post import PostQuery
from .project import ProjectQuery
from .project_health_metrics import ProjectHealthMetricsQuery
from .snapshot import SnapshotQuery
from .sponsor import SponsorQuery
from .stats import StatsQuery


class OwaspQuery(
    ChapterQuery,
    CommitteeQuery,
    EventQuery,
    PostQuery,
    ProjectHealthMetricsQuery,
    ProjectQuery,
    SnapshotQuery,
    SponsorQuery,
    StatsQuery,
):
    """OWASP queries."""
