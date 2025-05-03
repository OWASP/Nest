"""A command to load OWASP Nest data."""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.utils.index import register_indexes, unregister_indexes


class Command(BaseCommand):
    help = "Load OWASP Nest data."

    def handle(self, *_args, **_options) -> None:
        """Load data into the OWASP Nest application."""
        # Disable indexing
        unregister_indexes()

        # Run loaddata
        with transaction.atomic():
            call_command("loaddata", "data/nest.json.gz", "-v", "3")

        # Enable indexing
        register_indexes()
