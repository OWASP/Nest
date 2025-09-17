"""Test cases for Nest calendar events utilities."""

from unittest.mock import patch

from django.utils import timezone

from apps.nest.models.reminder_schedule import ReminderSchedule
from apps.nest.utils.calendar_events import parse_reminder_args, update_reminder_schedule_date

REMINDER_ID = 4


class TestCalendarEventsUtils:
    """Test cases for Nest calendar events utilities."""

    def test_parse_reminder_args_all_args(self):
        """Test parse_reminder_args with all arguments provided."""
        text = (
            "--channel C123456 --event_number 1 --minutes_before 15 "
            '--message "Meeting with team" --recurrence weekly'
        )
        args = parse_reminder_args(text)
        assert args.channel == "C123456"
        assert args.event_number == 1
        assert args.minutes_before == 15
        assert args.message == ["Meeting with team"]
        assert args.recurrence == "weekly"

    def test_parse_reminder_args_missing_optional_args(self):
        """Test parse_reminder_args with only required arguments."""
        text = "--channel C123456 --event_number 2"
        args = parse_reminder_args(text)
        assert args.channel == "C123456"
        assert args.event_number == 2
        assert args.minutes_before == 10  # Default value
        assert args.message == []  # Default value
        assert args.recurrence == "once"  # Default value

    @patch("apps.nest.models.reminder_schedule.ReminderSchedule.objects.get")
    def test_update_reminder_schedule_date_once(self, mock_get):
        """Test update_reminder_schedule_date with 'once' recurrence (no update)."""
        reminder = ReminderSchedule(scheduled_time=timezone.now(), recurrence="once")
        original_time = reminder.scheduled_time
        mock_get.return_value = reminder
        update_reminder_schedule_date(REMINDER_ID)
        assert reminder.scheduled_time == original_time  # No change expected

    @patch("apps.nest.models.reminder_schedule.ReminderSchedule.objects.get")
    def test_update_reminder_schedule_date_future_date(self, mock_get):
        """Test update_reminder_schedule_date with a future scheduled_time (no update)."""
        future_time = timezone.now() + timezone.timedelta(days=1)
        reminder = ReminderSchedule(scheduled_time=future_time, recurrence="daily")
        original_time = reminder.scheduled_time
        mock_get.return_value = reminder
        update_reminder_schedule_date(REMINDER_ID)
        assert reminder.scheduled_time == original_time  # No change expected

    @patch("apps.nest.models.reminder_schedule.ReminderSchedule.objects.get")
    def test_update_reminder_schedule_date_nonexistent(self, mock_get):
        """Test update_reminder_schedule_date when ReminderSchedule does not exist."""
        mock_get.side_effect = ReminderSchedule.DoesNotExist
        # Should not raise an exception
        update_reminder_schedule_date(REMINDER_ID)
        mock_get.assert_called_once_with(pk=REMINDER_ID)

    @patch("apps.nest.models.reminder_schedule.ReminderSchedule.save")
    @patch("apps.nest.models.reminder_schedule.ReminderSchedule.objects.get")
    def test_update_reminder_schedule_date_daily(self, mock_get, mock_save):
        """Test update_reminder_schedule_date with 'daily' recurrence."""
        past_time = timezone.now() - timezone.timedelta(days=1)
        reminder = ReminderSchedule(scheduled_time=past_time, recurrence="daily")
        mock_get.return_value = reminder
        update_reminder_schedule_date(REMINDER_ID)
        expected_time = past_time + timezone.timedelta(days=1)
        assert reminder.scheduled_time == expected_time
        mock_save.assert_called_once_with(update_fields=["scheduled_time"])
        mock_get.assert_called_once_with(pk=REMINDER_ID)

    @patch("apps.nest.models.reminder_schedule.ReminderSchedule.save")
    @patch("apps.nest.models.reminder_schedule.ReminderSchedule.objects.get")
    def test_update_reminder_schedule_date_weekly(self, mock_get, mock_save):
        """Test update_reminder_schedule_date with 'weekly' recurrence."""
        past_time = timezone.now() - timezone.timedelta(weeks=1)
        reminder = ReminderSchedule(scheduled_time=past_time, recurrence="weekly")
        mock_get.return_value = reminder
        update_reminder_schedule_date(REMINDER_ID)
        expected_time = past_time + timezone.timedelta(weeks=1)
        assert reminder.scheduled_time == expected_time
        mock_save.assert_called_once_with(update_fields=["scheduled_time"])
        mock_get.assert_called_once_with(pk=REMINDER_ID)

    @patch("apps.nest.models.reminder_schedule.ReminderSchedule.save")
    @patch("apps.nest.models.reminder_schedule.ReminderSchedule.objects.get")
    def test_update_reminder_schedule_date_monthly(self, mock_get, mock_save):
        """Test update_reminder_schedule_date with 'monthly' recurrence."""
        past_time = timezone.now() - timezone.timedelta(days=30)
        reminder = ReminderSchedule(scheduled_time=past_time, recurrence="monthly")
        mock_get.return_value = reminder
        update_reminder_schedule_date(REMINDER_ID)
        expected_time = past_time.replace(month=(past_time.month + 1) % 12 or 12)
        assert reminder.scheduled_time == expected_time
        mock_save.assert_called_once_with(update_fields=["scheduled_time"])
        mock_get.assert_called_once_with(pk=REMINDER_ID)
