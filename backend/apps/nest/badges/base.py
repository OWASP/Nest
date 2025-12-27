"""Base badge handler module."""

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
        """Initialize the handler."""
        self.stdout = stdout
        self.style = style

    @abstractmethod
    def get_eligible_users(self) -> QuerySet[User]:
        """Return a QuerySet of users who should currently have this badge."""

    def get_badge_defaults(self) -> dict:
        """Return the default attributes for the badge."""
        return {
            "description": self.description,
            "css_class": self.css_class,
            "weight": self.weight,
        }

    def _log(self, message, style_func=None):
        """Log to both file logger and stdout if available."""
        logger.info(message)
        if self.stdout:
            if style_func:
                message = style_func(message)
            self.stdout.write(message)

    def process(self):
        """Execute the badge sync process."""
        if not self.name:
            msg = "Badge name must be defined."
            raise ValueError(msg)

        badge, created = Badge.objects.get_or_create(
            name=self.name,
            defaults=self.get_badge_defaults(),
        )

        if created:
            self._log(f"Created badge: '{badge.name}'")

        user_without_badge = self.get_eligible_users()
        users_to_add = user_without_badge.exclude(
            user_badges__badge=badge,
            user_badges__is_active=True,
        )

        added_count = 0
        for user in users_to_add:
            user_badge, created = UserBadge.objects.get_or_create(user=user, badge=badge)
            if not user_badge.is_active:
                user_badge.is_active = True
                user_badge.save(update_fields=["is_active"])
                added_count += 1

        self._log(f"Added '{self.name}' badge to {added_count} users")

        users_to_remove_badge = UserBadge.objects.filter(
            badge=badge,
            is_active=True,
        ).exclude(user__in=user_without_badge)

        count = users_to_remove_badge.count()
        if count:
            users_to_remove_badge.update(is_active=False)
            self._log(f"Removed '{self.name}' badge from {count} users")
