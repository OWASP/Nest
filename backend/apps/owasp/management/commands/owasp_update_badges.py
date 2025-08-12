"""Management command to sync badges for users based on their roles/attributes."""

import logging

from django.core.management.base import BaseCommand

from apps.github.models.user import User
from apps.owasp.models.badge import Badge

logger = logging.getLogger(__name__)

OWASP_STAFF_BADGE_NAME = "OWASP Staff"


class Command(BaseCommand):
    """Sync badges for users based on their roles and attributes."""

    help = "Sync badges for users based on their roles and attributes"

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Syncing user badges...")
        self.sync_owasp_staff_badge()
        self.stdout.write(self.style.SUCCESS("User badges sync completed"))

    def sync_owasp_staff_badge(self):
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

        # Assign badge to employees.
        employees_without_badge = User.objects.filter(is_owasp_employee=True).exclude(badges=badge)
        count = employees_without_badge.count()

        if count:
            badge.users.add(*employees_without_badge)

        logger.info("Added '%s' badge to %s users", OWASP_STAFF_BADGE_NAME, count)
        self.stdout.write(f"Added badge to {count} employees")

        # Remove badge from non-OWASP employees.
        non_employees = User.objects.filter(is_owasp_employee=False, badges=badge)
        removed_count = non_employees.count()

        if removed_count:
            badge.users.remove(*non_employees)

        logger.info("Removed '%s' badge from %s users", OWASP_STAFF_BADGE_NAME, removed_count)
        self.stdout.write(f"Removed badge from {removed_count} non-employees")
