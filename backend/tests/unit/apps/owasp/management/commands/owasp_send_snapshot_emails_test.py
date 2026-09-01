"""Tests for owasp_send_snapshot_emails management command."""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.owasp.models.snapshot import Snapshot


class TestSendSnapshotEmailsCommand:
    """Test owasp_send_snapshot_emails management command."""

    @patch("apps.owasp.management.commands.owasp_send_snapshot_emails.Snapshot.objects")
    def test_snapshot_not_found(self, mock_objects):
        """Test command raises CommandError when snapshot doesn't exist."""
        mock_objects.get.side_effect = Snapshot.DoesNotExist

        with pytest.raises(CommandError, match="not found"):
            call_command("owasp_send_snapshot_emails", "--snapshot-key=2026-W99")

    @patch("apps.owasp.management.commands.owasp_send_snapshot_emails.Snapshot.objects")
    def test_snapshot_not_completed(self, mock_objects):
        """Test command raises CommandError when snapshot is not completed."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.status = Snapshot.Status.PENDING
        mock_objects.get.return_value = mock_snapshot

        with pytest.raises(CommandError, match="not completed"):
            call_command("owasp_send_snapshot_emails", "--snapshot-key=2026-W30")

    @patch("apps.owasp.management.commands.owasp_send_snapshot_emails.django_rq")
    @patch(
        "apps.owasp.management.commands.owasp_send_snapshot_emails.SnapshotSubscription.objects"
    )
    @patch("apps.owasp.management.commands.owasp_send_snapshot_emails.EmailLog")
    @patch("apps.owasp.management.commands.owasp_send_snapshot_emails.Snapshot.objects")
    def test_dry_run(self, mock_snap_objects, mock_email_log, mock_snap_sub, mock_rq):
        """Test dry run doesn't enqueue jobs."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.status = Snapshot.Status.COMPLETED
        mock_snapshot.frequency = "weekly"
        mock_snap_objects.get.return_value = mock_snapshot

        mock_sub = MagicMock()
        mock_sub.user = "testuser"
        mock_qs = MagicMock()
        mock_qs.__iter__ = lambda _: iter([mock_sub])
        mock_qs.count.return_value = 1
        prefetch_result = mock_snap_sub.filter.return_value.select_related.return_value
        prefetch_result.prefetch_related.return_value = mock_qs

        mock_email_log.is_duplicate.return_value = False

        stdout = StringIO()
        call_command(
            "owasp_send_snapshot_emails", "--snapshot-key=2026-W30", "--dry-run", stdout=stdout
        )

        output = stdout.getvalue()
        assert "DRY RUN" in output
        mock_rq.get_queue.return_value.enqueue.assert_not_called()

    @patch("apps.owasp.management.commands.owasp_send_snapshot_emails.django_rq")
    @patch(
        "apps.owasp.management.commands.owasp_send_snapshot_emails.SnapshotSubscription.objects"
    )
    @patch("apps.owasp.management.commands.owasp_send_snapshot_emails.EmailLog")
    @patch("apps.owasp.management.commands.owasp_send_snapshot_emails.Snapshot.objects")
    def test_enqueues_digest_jobs(self, mock_snap_objects, mock_email_log, mock_snap_sub, mock_rq):
        """Test command enqueues RQ jobs for each active subscriber."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.status = Snapshot.Status.COMPLETED
        mock_snapshot.frequency = "weekly"
        mock_snapshot.id = 42
        mock_snap_objects.get.return_value = mock_snapshot

        mock_sub = MagicMock()
        mock_sub.user = "testuser"
        mock_sub.id = 7
        mock_qs = MagicMock()
        mock_qs.__iter__ = lambda _: iter([mock_sub])
        mock_qs.count.return_value = 1
        prefetch_result = mock_snap_sub.filter.return_value.select_related.return_value
        prefetch_result.prefetch_related.return_value = mock_qs

        mock_email_log.is_duplicate.return_value = False

        stdout = StringIO()
        call_command("owasp_send_snapshot_emails", "--snapshot-key=2026-W30", stdout=stdout)

        mock_rq.get_queue.assert_called_with("ai")
        mock_rq.get_queue.return_value.enqueue.assert_called_once()
        assert "ENQUEUED" in stdout.getvalue()

    @patch(
        "apps.owasp.management.commands.owasp_send_snapshot_emails.SnapshotSubscription.objects"
    )
    @patch("apps.owasp.management.commands.owasp_send_snapshot_emails.EmailLog")
    @patch("apps.owasp.management.commands.owasp_send_snapshot_emails.Snapshot.objects")
    def test_skips_already_sent(self, mock_snap_objects, mock_email_log, mock_snap_sub):
        """Test command skips already-sent subscribers."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.status = Snapshot.Status.COMPLETED
        mock_snapshot.frequency = "weekly"
        mock_snap_objects.get.return_value = mock_snapshot

        mock_sub = MagicMock()
        mock_sub.user = "testuser"
        mock_qs = MagicMock()
        mock_qs.__iter__ = lambda _: iter([mock_sub])
        mock_qs.count.return_value = 1
        prefetch_result = mock_snap_sub.filter.return_value.select_related.return_value
        prefetch_result.prefetch_related.return_value = mock_qs

        mock_email_log.is_duplicate.return_value = True

        stdout = StringIO()
        call_command("owasp_send_snapshot_emails", "--snapshot-key=2026-W30", stdout=stdout)

        assert "SKIP" in stdout.getvalue()
