"""Base command for badge management."""

import logging
from abc import ABC, abstractmethod

from django.core.management.base import BaseCommand
from django.db.models import QuerySet

from apps.github.models.user import User
from apps.nest.models.badge import Badge
from apps.nest.models.user_badge import UserBadge

logger = logging.getLogger(__name__)


class BaseBadgeCommand(BaseCommand, ABC):
    """Base class for badge sync commands."""

    badge_css_class: str | None = None
    badge_description: str | None = None
    badge_name: str | None = None
    badge_weight: int | None = None

    @abstractmethod
    def get_eligible_users(self) -> QuerySet[User]:
        """Return users who should have this badge."""

    def _log(self, message):
        logger.info(message)
        self.stdout.write(message)

    def handle(self, *args, **options):
        if not self.badge_name:
            msg = "Badge name must be set"
            raise ValueError(msg)

        self.stdout.write(f"Syncing {self.badge_name}...")

        try:
            badge, created = Badge.objects.get_or_create(
                name=self.badge_name,
                defaults={
                    "css_class": self.badge_css_class,
                    "description": self.badge_description,
                    "weight": self.badge_weight,
                },
            )

            if created:
                self._log(f"Created badge: '{badge.name}'")
            else:
                badge.description = self.badge_description
                badge.css_class = self.badge_css_class
                badge.weight = self.badge_weight
                badge.save(update_fields=["css_class", "description", "weight"])

            eligible_users = self.get_eligible_users()
            users_to_add = eligible_users.exclude(
                user_badges__badge=badge,
                user_badges__is_active=True,
            )

            new_badges = [
                UserBadge(user=user, badge=badge, is_active=True) for user in users_to_add
            ]

            if new_badges:
                UserBadge.objects.bulk_create(
                    new_badges,
                    update_conflicts=True,
                    update_fields=["is_active"],
                    unique_fields=["user", "badge"],
                )

            added_count = len(new_badges)

            if added_count > 0:
                user_word = "user" if added_count == 1 else "users"
                self._log(f"Added '{self.badge_name}' badge to {added_count} {user_word}")

            users_to_remove = UserBadge.objects.filter(
                badge=badge,
                is_active=True,
            ).exclude(user__in=eligible_users)

            removed_count = users_to_remove.count()
            if removed_count:
                users_to_remove.update(is_active=False)
                user_word = "user" if removed_count == 1 else "users"
                self._log(f"Removed '{self.badge_name}' badge from {removed_count} {user_word}")

            self.stdout.write(self.style.SUCCESS(f"{self.badge_name} synced successfully"))
        except Exception:
            logger.exception("Failed to sync %s", self.badge_name)
            self.stdout.write(self.style.ERROR(f"{self.badge_name} sync failed"))
            raise
