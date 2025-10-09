"""Test cases for Nest Calendar Events Base Scheduler."""

from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from apps.nest.schedulers.calendar_events.base import BaseScheduler


class TestBaseScheduler:
    """Test cases for the BaseScheduler class."""

    @patch("apps.nest.schedulers.calendar_events.base.get_scheduler")
    def test_init(self, mock_get_scheduler):
        """Test the initialization of BaseScheduler."""
        mock_reminder_schedule = MagicMock()
        scheduler_instance = MagicMock()
        mock_get_scheduler.return_value = scheduler_instance

        base_scheduler = BaseScheduler(reminder_schedule=mock_reminder_schedule)

        assert base_scheduler.reminder_schedule == mock_reminder_schedule
        assert base_scheduler.scheduler == scheduler_instance
        mock_get_scheduler.assert_called_once_with("default")

    @patch("apps.nest.schedulers.calendar_events.base.get_scheduler")
    def test_schedule_once(self, mock_get_scheduler):
        """Test scheduling a one-time reminder."""
        mock_reminder_schedule = MagicMock()
        mock_reminder_schedule.recurrence = "once"
        mock_reminder_schedule.scheduled_time = timezone.datetime(2024, 10, 10, 10, 0, 0)
        mock_reminder_schedule.reminder.message = "Test Message"
        mock_reminder_schedule.reminder.entity_channel = MagicMock()
        mock_reminder_schedule.reminder.entity_channel.pk = 5
        mock_reminder_schedule.pk = 1

        scheduler_instance = MagicMock()
        mock_get_scheduler.return_value = scheduler_instance

        base_scheduler = BaseScheduler(reminder_schedule=mock_reminder_schedule)
        base_scheduler.schedule()

        scheduler_instance.enqueue_at.assert_any_call(
            mock_reminder_schedule.scheduled_time,
            BaseScheduler.send_and_delete,
            message="Test Message",
            channel_id=5,
            reminder_schedule_id=mock_reminder_schedule.pk,
        )
        mock_reminder_schedule.save.assert_called_once_with(update_fields=["job_id"])

    @patch("apps.nest.schedulers.calendar_events.base.get_scheduler")
    def test_schedule_recurring(self, mock_get_scheduler):
        """Test scheduling a recurring reminder."""
        mock_reminder_schedule = MagicMock()
        mock_reminder_schedule.recurrence = "daily"
        mock_reminder_schedule.cron_expression = "0 9 * * *"
        mock_reminder_schedule.reminder.message = "Daily Reminder"
        mock_reminder_schedule.reminder.entity_channel.pk = 5
        mock_reminder_schedule.pk = 4

        scheduler_instance = MagicMock()
        mock_get_scheduler.return_value = scheduler_instance

        base_scheduler = BaseScheduler(reminder_schedule=mock_reminder_schedule)
        base_scheduler.schedule()

        scheduler_instance.cron.assert_called_once_with(
            "0 9 * * *",
            func=BaseScheduler.send_and_update,
            args=("Daily Reminder", 5, 4),
            queue_name="default",
            use_local_timezone=True,
            result_ttl=500,
        )
        mock_reminder_schedule.save.assert_called_once_with(update_fields=["job_id"])

    @patch("apps.nest.schedulers.calendar_events.base.get_scheduler")
    def test_cancel(self, mock_get_scheduler):
        """Test cancelling a scheduled reminder."""
        mock_reminder_schedule = MagicMock()
        mock_reminder_schedule.job_id = "job_123"

        scheduler_instance = MagicMock()

        mock_get_scheduler.return_value = scheduler_instance

        base_scheduler = BaseScheduler(reminder_schedule=mock_reminder_schedule)
        base_scheduler.cancel()

        scheduler_instance.cancel.assert_called_once_with("job_123")
        mock_reminder_schedule.reminder.delete.assert_called_once()

    def test_send_message_not_implemented(self):
        """Test that send_message raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            BaseScheduler.send_message("Test Message", "C123456")
        assert str(exc_info.value) == "Subclasses must implement this method."

    def test_send_and_delete_not_implemented(self):
        """Test that send_and_delete raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            BaseScheduler.send_and_delete("Test Message", 5, 4)
        assert str(exc_info.value) == "Subclasses must implement this method."

    def test_send_and_update_not_implemented(self):
        """Test that send_and_update raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            BaseScheduler.send_and_update("Test Message", 5, 4)
        assert str(exc_info.value) == "Subclasses must implement this method."
