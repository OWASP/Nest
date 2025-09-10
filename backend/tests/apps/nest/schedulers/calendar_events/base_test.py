"""Test cases for Nest Calendar Events Base Scheduler."""

from unittest.mock import MagicMock, patch

import pytest

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
        mock_reminder_schedule.scheduled_time = "2024-10-10 10:00:00"
        mock_reminder_schedule.reminder.message = "Test Message"
        mock_reminder_schedule.reminder.channel_id = "C123456"

        scheduler_instance = MagicMock()
        mock_get_scheduler.return_value = scheduler_instance

        base_scheduler = BaseScheduler(reminder_schedule=mock_reminder_schedule)
        base_scheduler.schedule()

        scheduler_instance.enqueue_at.assert_called_once_with(
            "2024-10-10 10:00:00",
            BaseScheduler.send_message,
            message="Test Message",
            channel_id="C123456",
        )

    @patch("apps.nest.schedulers.calendar_events.base.get_scheduler")
    def test_schedule_recurring(self, mock_get_scheduler):
        """Test scheduling a recurring reminder."""
        mock_reminder_schedule = MagicMock()
        mock_reminder_schedule.recurrence = "daily"
        mock_reminder_schedule.cron_expression = "0 9 * * *"
        mock_reminder_schedule.reminder.message = "Daily Reminder"
        mock_reminder_schedule.reminder.channel_id = "C123456"

        scheduler_instance = MagicMock()
        mock_get_scheduler.return_value = scheduler_instance

        base_scheduler = BaseScheduler(reminder_schedule=mock_reminder_schedule)
        base_scheduler.schedule()

        scheduler_instance.cron.assert_called_once_with(
            "0 9 * * *",
            func=BaseScheduler.send_message,
            args=("Daily Reminder", "C123456"),
            queue_name="default",
            use_local_timezone=True,
            result_ttl=500,
        )

    def test_send_message_not_implemented(self):
        """Test that send_message raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            BaseScheduler.send_message("Test Message", "C123456")
        assert str(exc_info.value) == "Subclasses must implement this method."
