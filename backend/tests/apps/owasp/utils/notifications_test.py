"""Tests for notification utils."""

from unittest.mock import MagicMock, patch

from apps.owasp.utils.notifications import (
    publish_chapter_notification,
    publish_event_notification,
    publish_snapshot_notification,
)


class TestPublishSnapshotNotification:
    """Test publish_snapshot_notification."""

    @patch("apps.owasp.utils.notifications.get_redis_connection")
    def test_publishes_to_redis_stream(self, mock_redis):
        """Test that snapshot notification is published to Redis stream."""
        mock_conn = MagicMock()
        mock_redis.return_value = mock_conn
        snapshot = MagicMock()
        snapshot.id = 1

        publish_snapshot_notification(snapshot)

        mock_conn.xadd.assert_called_once()
        call_args = mock_conn.xadd.call_args
        assert call_args[0][0] == "owasp_notifications"
        assert call_args[0][1]["type"] == "snapshot_published"
        assert call_args[0][1]["snapshot_id"] == "1"

    @patch("apps.owasp.utils.notifications.get_redis_connection")
    def test_handles_redis_error(self, mock_redis):
        """Test that Redis connection errors are handled gracefully."""
        mock_redis.side_effect = Exception("Redis connection failed")
        snapshot = MagicMock()
        snapshot.id = 1

        publish_snapshot_notification(snapshot)  # Should not raise


class TestPublishChapterNotification:
    """Test publish_chapter_notification."""

    @patch("apps.owasp.utils.notifications.get_redis_connection")
    def test_publishes_created_notification(self, mock_redis):
        """Test that chapter created notification is published."""
        mock_conn = MagicMock()
        mock_redis.return_value = mock_conn
        chapter = MagicMock()
        chapter.id = 5

        publish_chapter_notification(chapter, "created")

        mock_conn.xadd.assert_called_once()
        call_args = mock_conn.xadd.call_args
        assert call_args[0][1]["type"] == "chapter_created"
        assert call_args[0][1]["chapter_id"] == "5"

    @patch("apps.owasp.utils.notifications.get_redis_connection")
    def test_publishes_updated_notification(self, mock_redis):
        """Test that chapter updated notification is published."""
        mock_conn = MagicMock()
        mock_redis.return_value = mock_conn
        chapter = MagicMock()
        chapter.id = 5

        publish_chapter_notification(chapter, "updated")

        call_args = mock_conn.xadd.call_args
        assert call_args[0][1]["type"] == "chapter_updated"

    @patch("apps.owasp.utils.notifications.get_redis_connection")
    def test_handles_redis_error(self, mock_redis):
        """Test that Redis errors are handled gracefully."""
        mock_redis.side_effect = Exception("Redis down")
        chapter = MagicMock()
        chapter.id = 5

        publish_chapter_notification(chapter, "created")  # Should not raise


class TestPublishEventNotification:
    """Test publish_event_notification."""

    @patch("apps.owasp.utils.notifications.get_redis_connection")
    def test_publishes_created_notification(self, mock_redis):
        """Test that event created notification is published."""
        mock_conn = MagicMock()
        mock_redis.return_value = mock_conn
        event = MagicMock()
        event.id = 10

        publish_event_notification(event, "created")

        call_args = mock_conn.xadd.call_args
        assert call_args[0][1]["type"] == "event_created"
        assert call_args[0][1]["event_id"] == "10"

    @patch("apps.owasp.utils.notifications.get_redis_connection")
    def test_publishes_updated_notification(self, mock_redis):
        """Test that event updated notification is published."""
        mock_conn = MagicMock()
        mock_redis.return_value = mock_conn
        event = MagicMock()
        event.id = 10

        publish_event_notification(event, "updated")

        call_args = mock_conn.xadd.call_args
        assert call_args[0][1]["type"] == "event_updated"

    @patch("apps.owasp.utils.notifications.get_redis_connection")
    def test_publishes_deadline_reminder_notification(self, mock_redis):
        """Test that event deadline reminder notification is published."""
        mock_conn = MagicMock()
        mock_redis.return_value = mock_conn
        event = MagicMock()
        event.id = 10

        publish_event_notification(event, "deadline_reminder", days_remaining=5)

        call_args = mock_conn.xadd.call_args
        assert call_args[0][1]["type"] == "event_deadline_reminder"
        assert call_args[0][1]["days_remaining"] == "5"

    @patch("apps.owasp.utils.notifications.get_redis_connection")
    def test_handles_redis_error(self, mock_redis):
        """Test that Redis errors are handled gracefully."""
        mock_redis.side_effect = Exception("Redis down")
        event = MagicMock()
        event.id = 10

        publish_event_notification(event, "created")  # Should not raise
