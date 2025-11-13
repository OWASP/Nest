"""A command to load OWASP Nest data."""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.utils import index


class Command(BaseCommand):
    help = "Load OWASP Nest data."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "--fixture-path",
            default="data/nest.json.gz",
            required=False,
            type=str,
            help="Path to the fixture file",
        )

    def handle(self, *_args, **_options) -> None:
        """Load data into the OWASP Nest application."""
        fixture_path = _options["fixture_path"]

        with index.disable_indexing(), transaction.atomic():
            # Run loaddata
            call_command("loaddata", fixture_path, "-v", "3")
