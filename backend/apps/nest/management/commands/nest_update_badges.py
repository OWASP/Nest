"""Management command to sync badges for users based on their roles/attributes."""

import logging

from django.core.management.base import BaseCommand

from apps.nest.badges import OWASPProjectLeaderBadgeHandler, OWASPStaffBadgeHandler

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Sync badges for users based on their roles and attributes."""

    help = "Sync badges for users based on their roles and attributes"

    BADGE_HANDLERS = {
        "staff": OWASPStaffBadgeHandler,
        "leader": OWASPProjectLeaderBadgeHandler,
    }

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--handler",
            type=str,
            choices=self.BADGE_HANDLERS.keys(),
            help="Specific badge handler to run. Runs all if omitted.",
            required=False,
        )

    def handle(self, *args, **options):
        """Execute the command."""
        handler_key = options.get("handler")

        if handler_key:
            self.stdout.write(f"Syncing specific badge: {handler_key}...")
            handlers_to_run = [self.BADGE_HANDLERS[handler_key]]
        else:
            self.stdout.write("Syncing ALL user badges...")
            handlers_to_run = self.BADGE_HANDLERS.values()

        failed_count = 0
        for handler_class in handlers_to_run:
            try:
                self.stdout.write(f"Processing badge: {handler_class.name}")
                handler = handler_class(stdout=self.stdout, style=self.style)
                handler.process()
            except Exception:
                logger.exception("Error processing badge %s", handler_class.name)
                self.stdout.write(self.style.ERROR(f"Failed to update {handler_class.name}"))
                failed_count += 1

        if failed_count:
            self.stdout.write(
                self.style.WARNING(f"User badges sync completed with {failed_count} failures.")
            )
        else:
            self.stdout.write(self.style.SUCCESS("User badges sync completed"))
