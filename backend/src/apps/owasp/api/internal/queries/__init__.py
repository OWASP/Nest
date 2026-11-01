"""OWASP GraphQL queries."""

from .board_of_directors import BoardOfDirectorsQuery
from .chapter import ChapterQuery
from .committee import CommitteeQuery
from .event import EventQuery
from .member_snapshot import MemberSnapshotQuery
from .post import PostQuery
from .project import ProjectQuery
from .project_health_metrics import ProjectHealthMetricsQuery
from .snapshot import SnapshotQuery
from .sponsor import SponsorQuery
from .stats import StatsQuery


class OwaspQuery(
    BoardOfDirectorsQuery,
    ChapterQuery,
    CommitteeQuery,
    EventQuery,
    MemberSnapshotQuery,
    PostQuery,
    ProjectHealthMetricsQuery,
    ProjectQuery,
    SnapshotQuery,
    SponsorQuery,
    StatsQuery,
):
    """OWASP queries."""
