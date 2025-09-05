"""Management command to sync badges for users based on their roles/attributes."""

import logging

from django.core.management.base import BaseCommand

from apps.github.models.user import User
from apps.nest.models.badge import Badge
from apps.nest.models.user_badge import UserBadge

logger = logging.getLogger(__name__)

OWASP_STAFF_BADGE_NAME = "OWASP Staff"


class Command(BaseCommand):
    """Sync badges for users based on their roles and attributes."""

    help = "Sync badges for users based on their roles and attributes"

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Syncing user badges...")
        self.update_owasp_staff_badge()
        self.stdout.write(self.style.SUCCESS("User badges sync completed"))

    def update_owasp_staff_badge(self):
        """Sync OWASP Staff badge for users."""
        # Get or create the OWASP Staff badge
        badge, created = Badge.objects.get_or_create(
            name=OWASP_STAFF_BADGE_NAME,
            defaults={
                "description": "Official OWASP Staff",
                "css_class": "fa-user-shield",
                "weight": 100,  # High weight for importance
            },
        )

        if created:
            logger.info("Created '%s' badge", OWASP_STAFF_BADGE_NAME)
            self.stdout.write(f"Created badge: {badge.name}")

        # Assign badge to employees who don't have it.
        employees_without_badge = User.objects.filter(is_owasp_staff=True).exclude(
            badges__badge=badge
        )
        count = employees_without_badge.count()

        if count:
            for user in employees_without_badge:
                user_badge, created = UserBadge.objects.get_or_create(user=user, badge=badge)
                if not user_badge.is_active:
                    user_badge.is_active = True
                    user_badge.save(update_fields=["is_active"])

        logger.info("Added '%s' badge to %s users", OWASP_STAFF_BADGE_NAME, count)
        self.stdout.write(f"Added badge to {count} employees")

        # Remove badge from non-OWASP employees.
        non_employees = User.objects.filter(
            is_owasp_staff=False,
            badges__badge=badge,
        ).distinct()
        removed_count = non_employees.count()

        if removed_count:
            UserBadge.objects.filter(
                user_id__in=non_employees.values_list("id", flat=True),
                badge=badge,
            ).update(is_active=False)

        logger.info("Removed '%s' badge from %s users", OWASP_STAFF_BADGE_NAME, removed_count)
        self.stdout.write(f"Removed badge from {removed_count} non-employees")
