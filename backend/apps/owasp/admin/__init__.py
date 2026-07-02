"""OWASP admin module initialization."""

from django.contrib import admin

from apps.owasp.models.project_health_requirements import ProjectHealthRequirements

from .board_of_directors import BoardOfDirectorsAdmin
from .certificate import CertificateAdmin
from .chapter import ChapterAdmin
from .committee import CommitteeAdmin
from .contribution_score import ContributionScoreAdmin
from .entity_channel import EntityChannelAdmin
from .entity_member import EntityMemberAdmin
from .event import EventAdmin
from .leaderboard_snapshot import LeaderboardSnapshotAdmin
from .member_profile import MemberProfileAdmin
from .member_snapshot import MemberSnapshotAdmin
from .post import PostAdmin
from .project import ProjectAdmin
from .project_health_metrics import ProjectHealthMetricsAdmin
from .scoring_weight import ScoringWeightAdmin
from .snapshot import SnapshotAdmin
from .sponsor import SponsorAdmin

admin.site.register(ProjectHealthRequirements)
