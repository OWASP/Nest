"""Sync OWASP Staff badges."""

from django.db.models import Q, QuerySet

from apps.github.models.user import User
from apps.nest.management.commands.base_badge_command import BaseBadgeCommand


class Command(BaseBadgeCommand):
    help = "Sync OWASP Staff badges"

    badge_css_class = "fa-user-shield"
    badge_description = "Official OWASP Staff"
    badge_name = "OWASP Staff"
    badge_weight = 100

    def get_eligible_users(self) -> QuerySet[User]:
        return User.objects.select_related("owasp_profile").filter(
            Q(owasp_profile__is_owasp_staff=True) | Q(is_owasp_staff=True)
        )
