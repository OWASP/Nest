"""Management command to sync badges for users based on their roles/attributes."""

import logging

from django.core.management.base import BaseCommand

from apps.nest.badges import OWASPProjectLeaderBadgeHandler, OWASPStaffBadgeHandler

logger = logging.getLogger(__name__)

# Constants for backward compatibility with existing tests
OWASP_STAFF_BADGE_NAME = "OWASP Staff"
OWASP_PROJECT_LEADER_BADGE_NAME = "OWASP Project Leader"


class Command(BaseCommand):
    """Sync badges for users based on their roles and attributes."""

    help = "Sync badges for users based on their roles and attributes"
    BADGE_HANDLERS = [
        OWASPStaffBadgeHandler,
        OWASPProjectLeaderBadgeHandler,
    ]

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Syncing user badges...")
        for handler_class in self.BADGE_HANDLERS:
            try:
                self.stdout.write(f"Processing badge: {handler_class.name}")
                handler = handler_class(stdout=self.stdout, style=self.style)
                handler.process()
            except Exception:
                logger.exception("Error processing badge %s", handler_class.name)
                self.stdout.write(self.style.ERROR(f"Failed to update {handler_class.name}"))

        self.stdout.write(self.style.SUCCESS("User badges sync completed"))
