"""Handler for the OWASP Project Leader badge.

This module manages the assignment and revocation of the OWASP Project Leader badge
based on users' leadership roles in OWASP projects.
"""

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from apps.github.models.user import User
from apps.nest.badges.base import BaseBadgeHandler
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project


class OWASPProjectLeaderBadgeHandler(BaseBadgeHandler):
    """Handler for managing the OWASP Project Leader badge.

    This badge is awarded to users who are active and reviewed leaders
    of OWASP projects. It uses the EntityMember model for users with the LEADER role.
    """

    name = "OWASP Project Leader"
    description = "Official OWASP Project Leader"
    css_class = "fa-user-shield"
    weight = 90

    def get_eligible_users(self) -> QuerySet[User]:
        """
        Get all users who should have the Project Leader badge.

        A user is eligible if they are an active, reviewed leader of at least
        one OWASP project.

        Returns:
            QuerySet of users who are project leaders.
        """

        # Get IDs of users who are active and reviewed project leaders
        leader_ids = EntityMember.objects.filter(
            entity_type=ContentType.objects.get_for_model(Project),
            role=EntityMember.Role.LEADER,
            is_active=True,
            is_reviewed=True,
            member__isnull=False,
        ).values_list("member_id", flat=True)
        return User.objects.filter(id__in=leader_ids).distinct()
