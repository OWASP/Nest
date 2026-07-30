"""OWASP GraphQL queries."""

from apps.owasp.api.internal.queries.board_candidate_claim import BoardCandidateClaimQuery
from apps.owasp.api.internal.queries.board_candidate_claim_evidence import (
    BoardCandidateClaimEvidenceQuery,
)

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
    BoardCandidateClaimEvidenceQuery,
    BoardCandidateClaimQuery,
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
