"""A command to load OWASP Nest data."""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.utils import index


class Command(BaseCommand):
    help = "Restore OWASP Nest data from a backup."

    def handle(self, *_args, **_options) -> None:
        """Restore OWASP Nest data."""
        with index.disable_indexing(), transaction.atomic():
            # Run loaddata
            call_command("loaddata", "data/backup.json.gz", "-v", "3")
