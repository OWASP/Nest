from unittest import mock

import pytest

from apps.nest.models import User
from apps.owasp.management.commands.owasp_run_notification_worker import Command
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
        snapshot.key = "2025-02"
        return snapshot

    @mock.patch("apps.owasp.utils.notifications.send_mail")
    @mock.patch("apps.owasp.utils.notifications.Notification")
    def test_send_notification_success(
        self, mock_notification, mock_send_mail, command, mock_user, mock_snapshot
    ):
        """Test successful notification sending."""
        mock_notification.objects.filter.return_value.exists.return_value = False

        from apps.owasp.utils.notifications import send_notification

        send_notification(
            user=mock_user,
            title=f"New Snapshot Published: {mock_snapshot.title}",
            message=f"Check out the latest OWASP snapshot: {mock_snapshot.title}",
            notification_type="snapshot_published",
            related_link=f"https://example.com/community/snapshots/{mock_snapshot.key}",
        )

        mock_send_mail.assert_called_once()
        mock_notification.objects.create.assert_called_once_with(
            recipient=mock_user,
            type="snapshot_published",
            title=f"New Snapshot Published: {mock_snapshot.title}",
            message=f"Check out the latest OWASP snapshot: {mock_snapshot.title}",
            related_link=f"https://example.com/community/snapshots/{mock_snapshot.key}",
        )

    @mock.patch("apps.owasp.utils.notifications.send_mail")
    @mock.patch("apps.owasp.utils.notifications.Notification")
    def test_send_notification_idempotency(
        self, mock_notification, mock_send_mail, command, mock_user, mock_snapshot
    ):
        """Test that notification is skipped if it already exists."""
        mock_notification.objects.filter.return_value.exists.return_value = True

        from apps.owasp.utils.notifications import send_notification

        send_notification(
            user=mock_user,
            title=f"New Snapshot Published: {mock_snapshot.title}",
            message=f"Check out the latest OWASP snapshot: {mock_snapshot.title}",
            notification_type="snapshot_published",
            related_link=f"https://example.com/community/snapshots/{mock_snapshot.key}",
        )

        mock_send_mail.assert_not_called()
        mock_notification.objects.create.assert_not_called()

    @mock.patch.object(Command, "process_message")
    def test_recover_pending_messages(self, mock_process, command):
        """Test recovery of pending messages."""
        redis_conn = mock.Mock()
        redis_conn.xautoclaim.return_value = (b"0-0", [(b"123-0", {b"data": b"test"})], [])

        command.recover_pending_messages(redis_conn, "stream", "group", "consumer")

        mock_process.assert_called_once()
        redis_conn.xack.assert_called_once_with("stream", "group", b"123-0")

    @mock.patch.object(Command, "process_message")
    def test_recover_pending_messages_failure(self, mock_process, command):
        """Test recovery failure moves message to DLQ."""
        redis_conn = mock.Mock()
        redis_conn.xautoclaim.return_value = (b"0-0", [(b"123-0", {b"data": b"test"})], [])

        mock_process.side_effect = Exception("Boom")

        command.recover_pending_messages(redis_conn, "stream", "group", "consumer")

        assert redis_conn.xadd.called
        assert redis_conn.xadd.call_args[0][0] == command.DLQ_STREAM_KEY
        redis_conn.xack.assert_called_once()


class TestProcessMessageRouting:
    """Test process_message routes new entity message types correctly."""

    @pytest.fixture
    def command(self):
        return Command()

    @pytest.mark.parametrize(
        ("msg_type", "handler_name"),
        [
            ("snapshot_published", "handle_snapshot_published"),
            ("chapter_created", "handle_chapter_created"),
            ("chapter_updated", "handle_chapter_updated"),
            ("event_created", "handle_event_created"),
            ("event_updated", "handle_event_updated"),
            ("event_deadline_reminder", "handle_event_deadline_reminder"),
        ],
    )
    def test_routes_to_correct_handler(self, command, msg_type, handler_name):
        """Test that each message type routes to the correct handler."""
        data = {b"type": msg_type.encode()}
        with mock.patch.object(command, handler_name) as mock_handler:
            command.process_message(data)
            mock_handler.assert_called_once_with(data)

    def test_unknown_message_type_does_not_raise(self, command):
        """Test that unknown message types are handled gracefully."""
        data = {b"type": b"unknown_type"}
        command.process_message(data)  # Should not raise


class TestEntityNotificationHandlers:
    """Test entity notification handler methods."""

    @pytest.fixture
    def command(self):
        return Command()

    @mock.patch(
        "apps.owasp.management.commands.owasp_run_notification_worker.get_redis_connection"
    )
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Subscription")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.ContentType")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Snapshot")
    def test_snapshot_published_queries_global_subscribers(
        self, mock_snapshot_cls, mock_ct, mock_sub, mock_redis
    ):
        """Test that snapshot_published queries global subscribers (object_id=0)."""
        command = Command()
        mock_redis.return_value = mock.MagicMock()
        mock_snapshot = mock.MagicMock()
        mock_snapshot.title = "Test Snapshot"
        mock_snapshot.key = "test-key"
        mock_snapshot_cls.objects.get.return_value = mock_snapshot
        mock_snapshot_cls.DoesNotExist = Exception
        mock_snapshot_cls.__name__ = "Snapshot"

        mock_content_type = mock.MagicMock()
        mock_ct.objects.get_for_model.return_value = mock_content_type

        # Mock subscriptions
        mock_sub.objects.filter.return_value.select_related.return_value = []

        data = {b"snapshot_id": b"99"}

        command.handle_snapshot_published(data)

        # Verify subscriptions queried with object_id=0
        mock_sub.objects.filter.assert_called_once_with(
            content_type=mock_content_type, object_id=0
        )

    @mock.patch(
        "apps.owasp.management.commands.owasp_run_notification_worker.get_redis_connection"
    )
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Subscription")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.ContentType")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Chapter")
    def test_chapter_created_queries_global_subscribers(
        self, mock_chapter_cls, mock_ct, mock_sub, mock_redis, command
    ):
        """Test that chapter_created queries subscribers with object_id=0."""
        mock_redis.return_value = mock.MagicMock()
        mock_chapter = mock.MagicMock()
        mock_chapter_cls.objects.get.return_value = mock_chapter
        mock_chapter_cls.DoesNotExist = Exception
        mock_chapter_cls.__name__ = "Chapter"

        mock_content_type = mock.MagicMock()
        mock_ct.objects.get_for_model.return_value = mock_content_type
        mock_sub.objects.filter.return_value.select_related.return_value = []

        data = {b"chapter_id": b"1"}
        command.handle_chapter_created(data)

        mock_sub.objects.filter.assert_called_once_with(
            content_type=mock_content_type, object_id=0
        )

    @mock.patch(
        "apps.owasp.management.commands.owasp_run_notification_worker.get_redis_connection"
    )
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Subscription")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.ContentType")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Chapter")
    def test_chapter_updated_queries_specific_subscribers(
        self, mock_chapter_cls, mock_ct, mock_sub, mock_redis, command
    ):
        """Test that chapter_updated queries subscribers with specific object_id."""
        mock_redis.return_value = mock.MagicMock()
        mock_chapter = mock.MagicMock()
        mock_chapter_cls.objects.get.return_value = mock_chapter
        mock_chapter_cls.DoesNotExist = Exception
        mock_chapter_cls.__name__ = "Chapter"

        mock_content_type = mock.MagicMock()
        mock_ct.objects.get_for_model.return_value = mock_content_type
        mock_sub.objects.filter.return_value.select_related.return_value = []

        data = {b"chapter_id": b"42"}
        command.handle_chapter_updated(data)

        mock_sub.objects.filter.assert_called_once_with(
            content_type=mock_content_type, object_id=42
        )

    @mock.patch(
        "apps.owasp.management.commands.owasp_run_notification_worker.get_redis_connection"
    )
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Subscription")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.ContentType")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Event")
    def test_event_created_queries_global_subscribers(
        self, mock_event_cls, mock_ct, mock_sub, mock_redis, command
    ):
        """Test that event_created queries subscribers with object_id=0."""
        mock_redis.return_value = mock.MagicMock()
        mock_event = mock.MagicMock()
        mock_event_cls.objects.get.return_value = mock_event
        mock_event_cls.DoesNotExist = Exception
        mock_event_cls.__name__ = "Event"

        mock_content_type = mock.MagicMock()
        mock_ct.objects.get_for_model.return_value = mock_content_type
        mock_sub.objects.filter.return_value.select_related.return_value = []

        data = {b"event_id": b"10"}
        command.handle_event_created(data)

        mock_sub.objects.filter.assert_called_once_with(
            content_type=mock_content_type, object_id=0
        )

    @mock.patch(
        "apps.owasp.management.commands.owasp_run_notification_worker.get_redis_connection"
    )
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Subscription")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.ContentType")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Event")
    def test_event_deadline_reminder_queries_specific_subscribers(
        self, mock_event_cls, mock_ct, mock_sub, mock_redis, command
    ):
        """Test that event_deadline_reminder queries subscribers with specific object_id."""
        mock_redis.return_value = mock.MagicMock()
        mock_event = mock.MagicMock()
        mock_event_cls.objects.get.return_value = mock_event
        mock_event_cls.DoesNotExist = Exception
        mock_event_cls.__name__ = "Event"

        mock_content_type = mock.MagicMock()
        mock_ct.objects.get_for_model.return_value = mock_content_type
        mock_sub.objects.filter.return_value.select_related.return_value = []

        data = {b"event_id": b"10"}
        command.handle_event_deadline_reminder(data)

        mock_sub.objects.filter.assert_called_once_with(
            content_type=mock_content_type, object_id=10
        )

    @mock.patch(
        "apps.owasp.management.commands.owasp_run_notification_worker.get_redis_connection"
    )
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Subscription")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.ContentType")
    @mock.patch("apps.owasp.management.commands.owasp_run_notification_worker.Event")
    def test_event_deadline_reminder_includes_days_remaining(
        self, mock_event_cls, mock_ct, mock_sub, mock_redis, command
    ):
        """Test that event_deadline_reminder includes days remaining in title/message."""
        mock_redis.return_value = mock.MagicMock()
        mock_event = mock.MagicMock()
        mock_event.name = "Test Event"
        mock_event_cls.objects.get.return_value = mock_event
        mock_event_cls.DoesNotExist = Exception
        mock_event_cls.__name__ = "Event"

        mock_content_type = mock.MagicMock()
        mock_ct.objects.get_for_model.return_value = mock_content_type

        # Mock a subscriber
        mock_user = mock.MagicMock(is_active=True)
        mock_sub_obj = mock.MagicMock()
        mock_sub_obj.user = mock_user
        mock_sub.objects.filter.return_value.select_related.return_value = [mock_sub_obj]

        data = {b"event_id": b"10", b"days_remaining": b"3"}

        with mock.patch.object(command, "send_notification_with_retry") as mock_send:
            command.handle_event_deadline_reminder(data)

            mock_send.assert_called_once()
            kwargs = mock_send.call_args[1]
            assert "(3 days left)" in kwargs["title"]
            assert "(3 days left)" in kwargs["message"]

    @mock.patch(
        "apps.owasp.management.commands.owasp_run_notification_worker.get_redis_connection"
    )
    def test_missing_entity_id_returns_early(self, mock_redis, command):
        """Test that messages without entity ID are handled gracefully."""
        mock_redis.return_value = mock.MagicMock()
        data = {b"type": b"chapter_created"}
        command.handle_chapter_created(data)  # Should not raise
