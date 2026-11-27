"""OWASP admin module initialization."""

from django.contrib import admin

from apps.owasp.models.project_health_requirements import ProjectHealthRequirements

from .board_discussion import BoardDiscussionAdmin
from .board_meeting import BoardMeetingAdmin
from .board_meeting_action import BoardMeetingActionAdmin
from .board_motion import BoardMotionAdmin
from .board_of_directors import BoardOfDirectorsAdmin
from .board_outcome import BoardOutcomeAdmin
from .board_vote import BoardVoteAdmin
from .certificate import CertificateAdmin
from .chapter import ChapterAdmin
from .committee import CommitteeAdmin
from .contribution_score import ContributionScoreAdmin
from .email_log import EmailLogAdmin
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
from .snapshot_feedback import SnapshotFeedbackAdmin
from .snapshot_subscription import SnapshotSubscriptionAdmin
from .sponsor import SponsorAdmin

admin.site.register(ProjectHealthRequirements)
