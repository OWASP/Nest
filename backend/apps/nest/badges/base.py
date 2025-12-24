import logging
from abc import ABC, abstractmethod

from django.db.models import QuerySet

from apps.github.models.user import User
from apps.nest.models.badge import Badge
from apps.nest.models.user_badge import UserBadge

logger = logging.getLogger(__name__)


class BaseBadgeHandler(ABC):
    """Base class for handling badge updates."""

    name: str
    description: str
    css_class: str
    weight: int

    def __init__(self, stdout=None, style=None):
        self.stdout = stdout
        self.style = style

    @abstractmethod
    def get_eligible_users(self) -> QuerySet[User]:
        """
        Return a QuerySet of users who should currently have this badge.
        """
        pass

    def get_badge_defaults(self) -> dict:
        return {
            "description": self.description,
            "css_class": self.css_class,
            "weight": self.weight,
        }

    def _log(self, message, style_func=None):
        """Helper to log to both file logger and stdout if available."""
        logger.info(message)
        if self.stdout:
            if style_func:
                message = style_func(message)
            self.stdout.write(message)

    def process(self):
        """
        Main execution method to sync the badge.
        1. Creates/Updates the Badge definition.
        2. Assigns badge to eligible users.
        3. Revokes badge from ineligible users.
        """
        if not self.name:
            raise ValueError("Badge name must be defined.")

        # 1. Get or Create the Badge
        badge, created = Badge.objects.get_or_create(
            name=self.name,
            defaults=self.get_badge_defaults(),
        )

        if created:
            self._log(f"Created badge: '{badge.name}'")

        # 2. Assign Badge to Eligible Users
        eligible_users_qs = self.get_eligible_users()
        
        # Filter for users who are eligible but don't have the badge actively assigned
        users_to_add = eligible_users_qs.exclude(
            user_badges__badge=badge,
            user_badges__is_active=True
        )
        
        added_count = 0
        for user in users_to_add:
            user_badge, _ = UserBadge.objects.get_or_create(user=user, badge=badge)
            if not user_badge.is_active:
                user_badge.is_active = True
                user_badge.save(update_fields=["is_active"])
                added_count += 1

        self.stdout.write(f"Added '{self.name}' badge to {added_count} users")
        if added_count:
            self._log(f"Added '{self.name}' badge to {added_count} users")

        # 3. Revoke Badge from Ineligible Users
        # Users who have the badge active, but are NOT in the eligible queryset
        users_to_revoke = UserBadge.objects.filter(
            badge=badge,
            is_active=True
        ).exclude(user__in=eligible_users_qs)

        revoked_count = users_to_revoke.count()
        if revoked_count:
            users_to_revoke.update(is_active=False)
            self._log(f"Removed '{self.name}' badge from {revoked_count} users")