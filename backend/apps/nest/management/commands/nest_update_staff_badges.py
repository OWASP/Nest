"""Sync OWASP Staff badges."""

from django.db.models import QuerySet

from apps.github.models.user import User
from apps.nest.management.commands.base_badge_command import BaseBadgeCommand


class Command(BaseBadgeCommand):
    help = "Sync OWASP Staff badges"

    badge_css_class = "ribbon"
    badge_description = "Official OWASP Staff"
    badge_name = "OWASP Staff"
    badge_weight = 100

    def get_eligible_users(self) -> QuerySet[User]:
        return User.objects.filter(is_owasp_staff=True)
