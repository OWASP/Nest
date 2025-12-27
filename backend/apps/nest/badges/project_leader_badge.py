"""Handler for the OWASP Project Leader badge."""

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from apps.github.models.user import User
from apps.nest.badges.base import BaseBadgeHandler
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project


class OWASPProjectLeaderBadgeHandler(BaseBadgeHandler):
    """Handler for managing the OWASP Project Leader badge."""

    name = "OWASP Project Leader"
    description = "Official OWASP Project Leader"
    css_class = "fa-user-shield"
    weight = 90

    def get_eligible_users(self) -> QuerySet[User]:
        """Get all users who should have the Project Leader badge.

        Returns:
            QuerySet of users who are project leaders.

        """
        leader_ids = EntityMember.objects.filter(
            entity_type=ContentType.objects.get_for_model(Project),
            role=EntityMember.Role.LEADER,
            is_active=True,
            is_reviewed=True,
            member__isnull=False,
        ).values_list("member_id", flat=True)
        return User.objects.filter(id__in=leader_ids).distinct()
