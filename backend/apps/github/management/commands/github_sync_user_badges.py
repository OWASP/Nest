"""Management command to sync badges for users based on their roles/attributes."""

import logging

from django.core.management.base import BaseCommand

from apps.github.models.user import User
from apps.owasp.models.badge import Badge

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Sync badges for users based on their roles and attributes."""

    help = "Sync badges for users based on their roles and attributes"

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Syncing user badges...")
        self.sync_owasp_employee_badge()
        self.stdout.write(self.style.SUCCESS("User badges sync completed"))

    def sync_owasp_employee_badge(self):
        """Sync OWASP Employee badge for users."""
        # Get or create the OWASP Employee badge
        badge, created = Badge.objects.get_or_create(
            name="OWASP Employee",
            defaults={
                "description": "Official OWASP Employee",
                "css_class": "fa-user-shield",
                "weight": 100,  # High weight for importance
            },
        )

        if created:
            logger.info("Created 'OWASP Employee' badge")
            self.stdout.write(f"Created badge: {badge.name}")

        # Add badge to OWASP employees
        employees = User.objects.filter(is_owasp_employee=True)
        count = 0

        for user in employees:
            # Check if the user already has the badge
            if not user.badges.filter(id=badge.id).exists():
                user.badges.add(badge)
                count += 1

        if count:
            logger.info("Added 'OWASP Employee' badge to %s users", count)
            self.stdout.write(f"Added badge to {count} employees")

        # Remove badge from non-OWASP employees
        non_employees = User.objects.filter(is_owasp_employee=False).filter(badges=badge)
        removed_count = non_employees.count()

        for user in non_employees:
            user.badges.remove(badge)

        if removed_count:
            logger.info("Removed 'OWASP Employee' badge from %s users", removed_count)
            self.stdout.write(f"Removed badge from {removed_count} non-employees")
