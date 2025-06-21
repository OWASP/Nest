"""A command to load OWASP Nest data."""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.utils.index import register_indexes, unregister_indexes


class Command(BaseCommand):
    help = "Restore OWASP Nest data from a backup."

    def handle(self, *_args, **_options) -> None:
        """Restore OWASP Nest data."""
        # Disable indexing
        unregister_indexes()

        # Run loaddata
        with transaction.atomic():
            call_command("loaddata", "data/backup.json.gz", "-v", "3")

        # Enable indexing
        register_indexes()
