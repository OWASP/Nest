"""Django management command for processing OWASP snapshots."""

import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.github.models.issue import Issue
from apps.github.models.release import Release
from apps.github.models.user import User
from apps.owasp.exceptions import SnapshotProcessingError
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project
from apps.owasp.models.snapshot import Snapshot

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Process pending snapshots and populate them with new data"

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        try:
            self.process_snapshots()
        except Exception as e:
            error_msg = f"Failed to process snapshot: {e}"
            raise SnapshotProcessingError(error_msg) from e

    def process_snapshots(self) -> None:
        """Process all pending snapshots."""
        pending_snapshots = Snapshot.objects.filter(status=Snapshot.Status.PENDING)

        if not pending_snapshots.exists():
            logger.info("No pending snapshots found")
            return

        for snapshot in pending_snapshots:
            try:
                with transaction.atomic():
                    self.process_snapshot(snapshot)
            except Exception as e:
                error_msg = f"Error processing snapshot {snapshot.id}: {e!s}"
                logger.exception(error_msg)
                snapshot.status = Snapshot.Status.ERROR
                snapshot.error_message = error_msg
                snapshot.save()

    def process_snapshot(self, snapshot: Snapshot) -> None:
        """Process a single snapshot.

        Args:
            snapshot (Snapshot): The snapshot instance to process.

        """
        logger.info(
            "Processing snapshot %s (%s to %s)",
            snapshot.id,
            snapshot.start_at,
            snapshot.end_at,
        )

        # Update status to processing
        snapshot.status = Snapshot.Status.PROCESSING
        snapshot.save()

        try:
            # Fetch new data for each model type
            new_chapters = Chapter.active_chapters.filter(
                created_at__gte=snapshot.start_at,
                created_at__lte=snapshot.end_at,
            )
            new_issues = Issue.snapshot_issues.filter(
                created_at__gte=snapshot.start_at,
                created_at__lte=snapshot.end_at,
            )
            new_projects = Project.active_projects.filter(
                created_at__gte=snapshot.start_at,
                created_at__lte=snapshot.end_at,
            )
            new_releases = Release.active_releases.filter(
                created_at__gte=snapshot.start_at,
                created_at__lte=snapshot.end_at,
            )
            new_users = User.snapshot_users.filter(
                created_at__gte=snapshot.start_at,
                created_at__lte=snapshot.end_at,
            )

            # Add items to snapshot
            snapshot.new_chapters.add(*new_chapters)
            snapshot.new_issues.add(*new_issues)
            snapshot.new_projects.add(*new_projects)
            snapshot.new_releases.add(*new_releases)
            snapshot.new_users.add(*new_users)

            # Update status to completed
            snapshot.status = Snapshot.Status.COMPLETED
            snapshot.save()

            logger.info("Successfully processed snapshot %s", snapshot.id)
            logger.info(
                "Added: %s chapters, %s projects, %s issues, %s releases, %s users",
                new_chapters.count(),
                new_projects.count(),
                new_issues.count(),
                new_releases.count(),
                new_users.count(),
            )

        except Exception as e:
            error_msg = f"Failed to process snapshot: {e}"
            raise SnapshotProcessingError(error_msg) from e
