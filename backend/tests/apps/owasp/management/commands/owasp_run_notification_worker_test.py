from unittest import mock
import pytest
from django.core.exceptions import ObjectDoesNotExist
from apps.owasp.management.commands.owasp_run_notification_worker import Command
from apps.nest.models import User
from apps.owasp.models.notification import Notification
from apps.owasp.models.snapshot import Snapshot
 
class TestOwaspRunNotificationWorker:
    @pytest.fixture
    def command(self):
        return Command()

    @pytest.fixture
    def mock_user(self):
        user = mock.MagicMock(spec=User)
        user.email = "test@example.com"
        user.id = 123
        return user

    @pytest.fixture
    def mock_snapshot(self):
        snapshot = mock.MagicMock(spec=Snapshot)
        snapshot.title = "Test Snapshot"
        snapshot.id = 456
        return snapshot

    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.send_mail")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Notification")
    def test_send_notification_success(self, mock_notification, mock_send_mail, command, mock_user, mock_snapshot):
        """Test successful notification sending."""
        mock_notification.objects.filter.return_value.exists.return_value = False

        command.send_notification(mock_user, mock_snapshot)

        mock_send_mail.assert_called_once()
        mock_notification.objects.create.assert_called_once_with(
            recipient=mock_user,
            type="snapshot_published",
            title=f"New Snapshot Published: {mock_snapshot.title}",
            message=f"Check out the latest OWASP snapshot: {mock_snapshot.title}",
            related_link=f"http://localhost:8000/community/snapshots/{mock_snapshot.id}",
        )

    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.send_mail")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Notification")
    def test_send_notification_idempotency(self, mock_notification, mock_send_mail, command, mock_user, mock_snapshot):
        """Test that notification is skipped if it already exists."""
        mock_notification.objects.filter.return_value.exists.return_value = True

        command.send_notification(mock_user, mock_snapshot)

        mock_send_mail.assert_not_called()
        mock_notification.objects.create.assert_not_called()

    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.User")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Snapshot")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Command.send_notification")
    def test_process_dlq_success(self, mock_send_notify, mock_snapshot_model, mock_user_model, command, mock_user, mock_snapshot):
        """Test successful DLQ processing."""
        redis_conn = mock.Mock()
        redis_conn.lock.return_value.acquire.return_value = True
        
        # Mock message data
        redis_conn.xrange.return_value = [
            (b"123-0", {b"user_id": b"123", b"snapshot_id": b"456"})
        ]

        mock_user_model.objects.get.return_value = mock_user
        mock_snapshot_model.objects.get.return_value = mock_snapshot

        command.process_dlq(redis_conn)

        mock_send_notify.assert_called_once_with(mock_user, mock_snapshot)
        redis_conn.xdel.assert_called_with(command.DLQ_STREAM_KEY, b"123-0")

    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.User")
    def test_process_dlq_missing_object(self, mock_user, command):
        """Test DLQ processing handles ObjectDoesNotExist by removing message."""
        redis_conn = mock.Mock()
        redis_conn.lock.return_value.acquire.return_value = True
        
        redis_conn.xrange.return_value = [
            (b"123-0", {b"user_id": b"999", b"snapshot_id": b"456"})
        ]

        mock_user.objects.get.side_effect = ObjectDoesNotExist

        command.process_dlq(redis_conn)

        redis_conn.xdel.assert_called_with(command.DLQ_STREAM_KEY, b"123-0")

    def test_process_dlq_missing_fields(self, command):
        """Test DLQ processing handles messages with missing fields."""
        redis_conn = mock.Mock()
        redis_conn.lock.return_value.acquire.return_value = True

        # Missing user_id
        redis_conn.xrange.return_value = [
            (b"123-0", {b"snapshot_id": b"456"})
        ]

        command.process_dlq(redis_conn)

        redis_conn.xdel.assert_called_with(command.DLQ_STREAM_KEY, b"123-0")

    def test_process_dlq_recovery_failure(self, command):
        """Test DLQ processing handles recovery_failed messages by removing them."""
        redis_conn = mock.Mock()
        redis_conn.lock.return_value.acquire.return_value = True

        redis_conn.xrange.return_value = [
            (b"123-0", {
                b"type": b"recovery_failed",
                b"message_id": b"original-999",
                b"error": b"Something went wrong"
            })
        ]

        command.process_dlq(redis_conn)
        
        redis_conn.xdel.assert_called_with(command.DLQ_STREAM_KEY, b"123-0")

    @mock.patch.object(Command, "process_message")
    def test_recover_pending_messages(self, mock_process, command):
        """Test recovery of pending messages."""
        redis_conn = mock.Mock()
        redis_conn.xautoclaim.return_value = (
            b"0-0",
            [
                (b"123-0", {b"data": b"test"})
            ],
            []
        )

        command.recover_pending_messages(redis_conn, "stream", "group", "consumer")

        mock_process.assert_called_once()
        redis_conn.xack.assert_called_once_with("stream", "group", b"123-0")

    @mock.patch.object(Command, "process_message")
    def test_recover_pending_messages_failure(self, mock_process, command):
        """Test recovery failure moves message to DLQ."""
        redis_conn = mock.Mock()
        redis_conn.xautoclaim.return_value = (
            b"0-0",
            [(b"123-0", {b"data": b"test"})],
            []
        )
        
        mock_process.side_effect = Exception("Boom")

        command.recover_pending_messages(redis_conn, "stream", "group", "consumer")
       
        assert redis_conn.xadd.called
        assert redis_conn.xadd.call_args[0][0] == command.DLQ_STREAM_KEY
        redis_conn.xack.assert_called_once()

    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.User")
    def test_process_dlq_retry_increment(self, mock_user, command):
        """Test that DLQ processing increments retry count and re-adds on failure."""
        redis_conn = mock.Mock()
        redis_conn.lock.return_value.acquire.return_value = True

        redis_conn.xrange.return_value = [
            (b"123-0", {b"user_id": b"123", b"snapshot_id": b"456", b"dlq_retries": b"1"})
        ]

        
        mock_user.objects.get.side_effect = Exception("Temp Error")

        command.process_dlq(redis_conn)

        # Should be deleted and re-added with count 2
        redis_conn.xdel.assert_called_with(command.DLQ_STREAM_KEY, b"123-0")
        assert redis_conn.xadd.called
        new_msg = redis_conn.xadd.call_args[0][1]
        assert new_msg["dlq_retries"] == "2"

    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.User")
    def test_process_dlq_max_retries_exceeded(self, mock_user, command):
        """Test that DLQ processing drops message after max retries."""
        redis_conn = mock.Mock()
        redis_conn.lock.return_value.acquire.return_value = True

        # Already at max retries (5)
        redis_conn.xrange.return_value = [
            (b"123-0", {b"user_id": b"123", b"snapshot_id": b"456", b"dlq_retries": b"5"})
        ]

        mock_user.objects.get.side_effect = Exception("Final Error")

        command.process_dlq(redis_conn)
   
        redis_conn.xdel.assert_called_with(command.DLQ_STREAM_KEY, b"123-0")        
        assert redis_conn.xadd.call_count == 0
