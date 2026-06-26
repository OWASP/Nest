"""Django management command for creating OWASP community snapshots."""

import logging
from datetime import UTC, datetime, timedelta

from django.core.management.base import BaseCommand

from apps.owasp.models.snapshot import Snapshot

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to create a community snapshot with automatic date range calculation."""

    help = "Create a community snapshot for a given frequency (weekly or monthly)"

    def add_arguments(self, parser):
        """Add command-line arguments.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "--frequency",
            type=str,
            choices=[Snapshot.Frequency.WEEKLY, Snapshot.Frequency.MONTHLY],
            default=Snapshot.Frequency.WEEKLY,
            help="Snapshot frequency: weekly (default) or monthly.",
        )

    def handle(self, *args, **options):
        """Handle command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        frequency = options["frequency"]
        start_at, end_at = self.calculate_date_range(frequency)

        self.stdout.write(f"Creating {frequency} snapshot")
        self.stdout.write(f"Period: {start_at.date()} to {end_at.date()}")
        logger.info(
            "Creating %s snapshot from %s to %s",
            frequency,
            start_at.date(),
            end_at.date(),
        )

        # Generate key to check for duplicates before creating.
        key = self.generate_key(start_at, frequency)
        if Snapshot.objects.filter(key=key).exists():
            self.stdout.write(
                self.style.WARNING(f"Snapshot with key '{key}' already exists, skipping creation")
            )
            logger.info("Snapshot with key '%s' already exists, skipping", key)
            return

        snapshot = Snapshot.objects.create(
            key=key,
            start_at=start_at,
            end_at=end_at,
            title=self.generate_title(start_at, frequency),
            status=Snapshot.Status.PENDING,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Snapshot created successfully (ID: {snapshot.id}, key: {snapshot.key})"
            )
        )
        logger.info(
            "Snapshot created: id=%s, key=%s, frequency=%s",
            snapshot.id,
            snapshot.key,
            frequency,
        )

    @staticmethod
    def calculate_date_range(frequency):
        """Calculate the start and end dates for the snapshot period.

        Args:
            frequency (str): The snapshot frequency (weekly or monthly).

        Returns:
            tuple[datetime, datetime]: A tuple of (start_at, end_at) datetimes.

        """
        current = datetime.now(tz=UTC)

        if frequency == Snapshot.Frequency.WEEKLY:
            # Last week: Monday 00:00:00 to Sunday 23:59:59
            days_since_monday = current.weekday()
            last_monday = current - timedelta(days=days_since_monday + 7)
            start_at = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_at = start_at + timedelta(days=6, hours=23, minutes=59, seconds=59)
        else:
            # Last month: 1st 00:00:00 to last day 23:59:59
            first_of_current_month = current.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end_at = first_of_current_month - timedelta(seconds=1)
            start_at = end_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        return start_at, end_at

    @staticmethod
    def generate_key(start_at, frequency):
        """Generate the snapshot key based on the start date and frequency.

        This mirrors the logic in the Snapshot model's save() method.

        Args:
            start_at (datetime): The start date of the snapshot period.
            frequency (str): The snapshot frequency (weekly or monthly).

        Returns:
            str: The generated snapshot key.

        """
        if frequency == Snapshot.Frequency.WEEKLY:
            iso_year, iso_week, _ = start_at.isocalendar()
            return f"{iso_year}-W{iso_week:02d}"
        return start_at.strftime("%Y-%m")

    @staticmethod
    def generate_title(start_at, frequency):
        """Generate a human-readable title for the snapshot.

        Args:
            start_at (datetime): The start date of the snapshot period.
            frequency (str): The snapshot frequency (weekly or monthly).

        Returns:
            str: The generated snapshot title.

        """
        if frequency == Snapshot.Frequency.WEEKLY:
            iso_year, iso_week, _ = start_at.isocalendar()
            return f"Week {iso_week} {iso_year} OWASP Community Snapshot"
        return f"{start_at.strftime('%B %Y')} OWASP Community Snapshot"
