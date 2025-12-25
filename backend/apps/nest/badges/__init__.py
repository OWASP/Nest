"""Badge handlers package for managing user badges."""

from apps.nest.badges.project_leader_badge import OWASPProjectLeaderBadgeHandler
from apps.nest.badges.staff_badge import OWASPStaffBadgeHandler

__all__ = [
    "OWASPProjectLeaderBadgeHandler",
    "OWASPStaffBadgeHandler",
]
