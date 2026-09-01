"""Django management command for sending snapshot subscription digest emails."""

import logging

import django_rq
from django.core.management.base import BaseCommand

from apps.owasp.models.email_log import EmailLog
from apps.owasp.models.snapshot import Snapshot
from apps.owasp.models.snapshot_subscription import SnapshotSubscription
from apps.owasp.services.newsletter import send_digest_email

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to send snapshot digest emails to subscribers."""

    help = "Send snapshot digest emails to subscribers for a given snapshot"

    def add_arguments(self, parser):
        """Add command-line arguments.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "--snapshot-key",
            type=str,
            required=True,
            help="The key of the snapshot to send digests for (e.g., 2026-W27).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview which subscribers would receive emails without sending.",
        )

    def handle(self, *args, **options):
        """Execute the command.

        Args:
            args: Positional arguments (unused).
            options: Parsed keyword arguments from the command line.

        """
        snapshot_key = options["snapshot_key"]
        dry_run = options["dry_run"]

        try:
            snapshot = Snapshot.objects.get(key=snapshot_key)
        except Snapshot.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Snapshot '{snapshot_key}' not found."))
            return

        if snapshot.status != Snapshot.Status.COMPLETED:
            self.stderr.write(
                self.style.ERROR(
                    f"Snapshot '{snapshot_key}' is not completed (status: {snapshot.status})."
                )
            )
            return

        self.stdout.write(
            self.style.NOTICE(
                f"Sending snapshot digests for '{snapshot_key}' (frequency: {snapshot.frequency})."
            )
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no emails will be sent."))

        subscriptions = (
            SnapshotSubscription.objects.filter(
                is_active=True,
                frequency=snapshot.frequency,
            )
            .select_related("user")
            .prefetch_related(
                "subscribed_projects",
                "subscribed_chapters",
                "subscribed_committees",
            )
        )

        stats = {"enqueued": 0, "skipped": 0, "total": subscriptions.count()}

        self.stdout.write(f"  Snapshot subscriptions: {stats['total']}")

        for subscription in subscriptions:
            if EmailLog.is_duplicate(snapshot=snapshot, snapshot_subscription=subscription):
                stats["skipped"] += 1
                self.stdout.write(f"    [SKIP] {subscription.user} — already sent.")
                continue

            if dry_run:
                self.stdout.write(f"    [DRY RUN] Would enqueue digest for {subscription.user}")
                stats["enqueued"] += 1
                continue

            django_rq.get_queue("ai").enqueue(
                send_digest_email,
                snapshot_id=snapshot.id,
                subscription_id=subscription.id,
            )
            stats["enqueued"] += 1
            self.stdout.write(f"    [ENQUEUED] {subscription.user}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Enqueued: {stats['enqueued']}, Skipped: {stats['skipped']}, "
                f"Total: {stats['total']}."
            )
        )
