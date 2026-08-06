"""OWASP GraphQL queries."""

from .board_of_directors import BoardOfDirectorsQuery
from .chapter import ChapterQuery
from .committee import CommitteeQuery
from .entity_subscription import EntitySubscriptionQuery
from .event import EventQuery
from .member_snapshot import MemberSnapshotQuery
from .post import PostQuery
from .project import ProjectQuery
from .project_health_metrics import ProjectHealthMetricsQuery
from .snapshot import SnapshotQuery
from .snapshot_subscription import SnapshotSubscriptionQuery
from .sponsor import SponsorQuery
from .stats import StatsQuery


class OwaspQuery(
    BoardOfDirectorsQuery,
    ChapterQuery,
    CommitteeQuery,
    EntitySubscriptionQuery,
    EventQuery,
    MemberSnapshotQuery,
    PostQuery,
    ProjectHealthMetricsQuery,
    ProjectQuery,
    SnapshotQuery,
    SnapshotSubscriptionQuery,
    SponsorQuery,
    StatsQuery,
):
    """OWASP queries."""
