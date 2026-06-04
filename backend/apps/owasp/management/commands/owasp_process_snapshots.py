"""Django management command for processing OWASP snapshots."""

import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest
from apps.github.models.release import Release
from apps.github.models.user import User
from apps.owasp.exceptions import SnapshotProcessingError
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.event import Event
from apps.owasp.models.post import Post
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
            chapters = self.get_new_items(
                Chapter,
                snapshot.start_at,
                snapshot.end_at,
            ).filter(
                is_active=True,
            )
            events = self.get_new_items(
                Event,
                snapshot.start_at,
                snapshot.end_at,
                date_field="start_date",
            )
            issues = self.get_new_items(
                Issue,
                snapshot.start_at,
                snapshot.end_at,
            )
            posts = self.get_new_items(
                Post,
                snapshot.start_at,
                snapshot.end_at,
                date_field="published_at",
            )
            projects = self.get_new_items(
                Project,
                snapshot.start_at,
                snapshot.end_at,
            ).filter(
                is_active=True,
            )
            pull_requests = self.get_new_items(
                PullRequest,
                snapshot.start_at,
                snapshot.end_at,
            )
            releases = self.get_new_items(
                Release,
                snapshot.start_at,
                snapshot.end_at,
            ).filter(
                is_draft=False,
                is_pre_release=False,
            )
            users = self.get_new_items(
                User,
                snapshot.start_at,
                snapshot.end_at,
            )

            # Add items to snapshot
            snapshot.chapters.add(*chapters)
            snapshot.events.add(*events)
            snapshot.issues.add(*issues)
            snapshot.posts.add(*posts)
            snapshot.projects.add(*projects)
            snapshot.pull_requests.add(*pull_requests)
            snapshot.releases.add(*releases)
            snapshot.users.add(*users)

            # Update status to completed
            snapshot.status = Snapshot.Status.COMPLETED
            snapshot.save()

            logger.info("Successfully processed snapshot %s", snapshot.id)
            logger.info(
                "Added: %s chapters, %s events, %s issues, %s posts, "
                "%s projects, %s pull requests, %s releases, %s users",
                chapters.count(),
                events.count(),
                issues.count(),
                posts.count(),
                projects.count(),
                pull_requests.count(),
                releases.count(),
                users.count(),
            )

        except Exception as e:
            error_msg = f"Failed to process snapshot: {e}"
            raise SnapshotProcessingError(error_msg) from e

    def get_new_items(self, model, start_at, end_at, date_field="created_at"):
        """Get only newly created items within the given timeframe."""
        return model.objects.filter(
            **{
                f"{date_field}__gte": start_at,
                f"{date_field}__lte": end_at,
            }
        )
