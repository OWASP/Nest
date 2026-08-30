"""Tests for email log model."""

from unittest.mock import MagicMock, patch

from apps.owasp.models.email_log import EmailLog
from apps.owasp.models.snapshot import Snapshot
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


class TestEmailLog:
    """Test EmailLog model."""

    def test_str_representation(self):
        """Test string representation with snapshot subscription."""
        log = MagicMock(spec=EmailLog)
        sub = MagicMock(spec=SnapshotSubscription)
        sub.user = "testuser"
        log.snapshot_subscription = sub
        log.snapshot = MagicMock()
        log.snapshot.key = "2026-W30"
        log.status = EmailLog.Status.SENT

        result = EmailLog.__str__(log)
        assert "testuser" in result
        assert "2026-W30" in result
        assert "sent" in result

    def test_status_choices(self):
        """Test status choices are correctly defined."""
        assert EmailLog.Status.SENT == "sent"
        assert EmailLog.Status.FAILED == "failed"


class TestEmailLogIsDuplicate:
    """Test EmailLog.is_duplicate class method."""

    @patch("apps.owasp.models.email_log.EmailLog.objects")
    def test_is_duplicate_returns_true(self, mock_objects):
        """Test duplicate check returns True when log exists."""
        mock_objects.filter.return_value.exists.return_value = True
        snapshot = MagicMock(spec=Snapshot)
        subscription = MagicMock(spec=SnapshotSubscription)

        result = EmailLog.is_duplicate(snapshot=snapshot, snapshot_subscription=subscription)

        assert result is True
        mock_objects.filter.assert_called_once_with(
            snapshot=snapshot, snapshot_subscription=subscription
        )

    @patch("apps.owasp.models.email_log.EmailLog.objects")
    def test_is_not_duplicate(self, mock_objects):
        """Test non-duplicate returns False."""
        mock_objects.filter.return_value.exists.return_value = False
        snapshot = MagicMock(spec=Snapshot)
        subscription = MagicMock(spec=SnapshotSubscription)

        result = EmailLog.is_duplicate(snapshot=snapshot, snapshot_subscription=subscription)

        assert result is False


class TestEmailLogMarkSent:
    """Test EmailLog.mark_sent class method."""

    @patch("apps.owasp.models.email_log.EmailLog.objects")
    def test_mark_sent(self, mock_objects):
        """Test marking an email as sent."""
        snapshot = MagicMock(spec=Snapshot)
        subscription = MagicMock(spec=SnapshotSubscription)

        EmailLog.mark_sent(snapshot=snapshot, snapshot_subscription=subscription)

        mock_objects.create.assert_called_once_with(
            snapshot=snapshot,
            snapshot_subscription=subscription,
            status=EmailLog.Status.SENT,
        )


class TestEmailLogMarkFailed:
    """Test EmailLog.mark_failed class method."""

    @patch("apps.owasp.models.email_log.EmailLog.objects")
    def test_mark_failed_with_error_message(self, mock_objects):
        """Test marking an email as failed with error message."""
        snapshot = MagicMock(spec=Snapshot)
        subscription = MagicMock(spec=SnapshotSubscription)

        EmailLog.mark_failed(
            snapshot=snapshot,
            snapshot_subscription=subscription,
            error_message="SMTP connection timeout",
        )

        mock_objects.create.assert_called_once_with(
            snapshot=snapshot,
            snapshot_subscription=subscription,
            status=EmailLog.Status.FAILED,
            error_message="SMTP connection timeout",
        )

    @patch("apps.owasp.models.email_log.EmailLog.objects")
    def test_mark_failed_default_error(self, mock_objects):
        """Test marking an email as failed with default empty error."""
        snapshot = MagicMock(spec=Snapshot)
        subscription = MagicMock(spec=SnapshotSubscription)

        EmailLog.mark_failed(snapshot=snapshot, snapshot_subscription=subscription)

        mock_objects.create.assert_called_once_with(
            snapshot=snapshot,
            snapshot_subscription=subscription,
            status=EmailLog.Status.FAILED,
            error_message="",
        )


class TestEmailLogMeta:
    """Test EmailLog Meta configuration."""

    def test_unique_constraint_exists(self):
        """Test unique constraint for subscription + snapshot."""
        constraints = EmailLog._meta.constraints
        constraint_names = {c.name for c in constraints}
        assert "unique_email_per_subscription_snapshot" in constraint_names

    def test_db_table(self):
        """Test database table name."""
        assert EmailLog._meta.db_table == "owasp_email_logs"
