"""Sync OWASP Project Leader badges."""

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from apps.github.models.user import User
from apps.nest.management.commands.base_badge_command import BaseBadgeCommand
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project


class Command(BaseBadgeCommand):
    help = "Sync OWASP Project Leader badges"
    
    badge_name = "OWASP Project Leader"
    badge_description = "Official OWASP Project Leader"
    badge_css_class = "fa-user-shield"
    badge_weight = 90

    def get_eligible_users(self) -> QuerySet[User]:
        leader_ids = EntityMember.objects.filter(
            entity_type=ContentType.objects.get_for_model(Project),
            role=EntityMember.Role.LEADER,
            is_active=True,
            is_reviewed=True,
            member__isnull=False,
        ).values_list("member_id", flat=True)
        return User.objects.filter(id__in=leader_ids).distinct()
