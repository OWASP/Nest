"""Sync board activity from OWASP/www-board into Django models."""

from django.core.management.base import BaseCommand, CommandError

from apps.owasp.parsers.board_activity import sync
from apps.owasp.parsers.board_activity.sync import MAX_YEAR, MIN_YEAR, SyncStatus

MIN_MONTH = 1
MAX_MONTH = 12


class Command(BaseCommand):
    help = "Sync OWASP board meeting activity from the www-board repository."

    def add_arguments(self, parser):
        """Add command-line arguments.

        Args:
            parser (argparse.ArgumentParser): The argument parser.

        """
        parser.add_argument(
            "--year",
            type=int,
            help="Only sync files whose filename begins with this 4-digit year.",
        )
        parser.add_argument(
            "--month",
            type=int,
            help="Further restrict to a specific month (1-12). Requires --year.",
        )
        parser.add_argument(
            "--path",
            type=str,
            help="Sync only a single repo-relative file path (ignores --year/--month).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-parse even when the stored git blob SHA matches.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and log intended writes without persisting.",
        )

    def handle(self, *args, **options):
        """Run the board activity sync.

        Raises:
            CommandError: If --month or --year is invalid, or if any file failed to sync.

        """
        year = options.get("year")
        month = options.get("month")
        path = options.get("path")

        if not path:
            if month is not None and year is None:
                message = "--month requires --year."
                raise CommandError(message)

            if month is not None and not (MIN_MONTH <= month <= MAX_MONTH):
                message = f"--month must be between {MIN_MONTH} and {MAX_MONTH}."
                raise CommandError(message)

            if year is not None and not (MIN_YEAR <= year <= MAX_YEAR):
                message = f"--year must be a 4-digit value between {MIN_YEAR} and {MAX_YEAR}."
                raise CommandError(message)

        stats = sync.run(
            year=year,
            month=month,
            path=path,
            force=options.get("force", False),
            dry_run=options.get("dry_run", False),
        )

        summary = ", ".join(f"{k}={v}" for k, v in sorted(stats.counts.items())) or "no files"
        self.stdout.write(self.style.SUCCESS(f"Board activity sync: {summary}"))

        errored = stats.counts.get(SyncStatus.ERRORED, 0)
        if errored:
            message = f"Board activity sync had {errored} errored file(s)."
            raise CommandError(message)
