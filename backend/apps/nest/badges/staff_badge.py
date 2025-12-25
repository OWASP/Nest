"""Handler for the OWASP Staff badge."""

from django.db.models import QuerySet

from apps.github.models.user import User
from apps.nest.badges.base import BaseBadgeHandler


class OWASPStaffBadgeHandler(BaseBadgeHandler):
    """Handler for managing the OWASP Staff badge."""

    name = "OWASP Staff"
    description = "Official OWASP Staff"
    css_class = "fa-user-shield"
    weight = 100

    def get_eligible_users(self) -> QuerySet[User]:
        """Get all users who should have the OWASP Staff badge.

        Returns:
            QuerySet of users with is_owasp_staff=True.

        """
        return User.objects.filter(is_owasp_staff=True)
