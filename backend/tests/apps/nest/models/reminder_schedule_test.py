"""Test cases for ReminderSchedule model."""

from apps.nest.models.reminder import Reminder
from apps.nest.models.reminder_schedule import ReminderSchedule
from apps.slack.models.member import Member


class TestReminderScheduleModel:
    """Test cases for ReminderSchedule model."""

    def test_str_representation(self):
        """Test string representation of the ReminderSchedule model."""
        member = Member(slack_user_id="U123456", username="Test User")
        reminder = Reminder(
            member=member,
            channel_id="C123456",
            message="Test reminder",
        )
        schedule = ReminderSchedule(
            reminder=reminder,
            scheduled_time="2023-01-01T12:00:00Z",
            recurrence=ReminderSchedule.Recurrence.DAILY,
        )
        assert (
            str(schedule)
            == f"Schedule for {reminder} at {schedule.scheduled_time} ({schedule.recurrence})"
        )

    def test_verbose_names(self):
        """Test verbose names of the ReminderSchedule model."""
        member = Member(slack_user_id="U123456", username="Test User")
        reminder = Reminder(
            member=member,
            channel_id="C123456",
            message="Test reminder",
        )
        schedule = ReminderSchedule(
            reminder=reminder,
            scheduled_time="2023-01-01T12:00:00Z",
            recurrence=ReminderSchedule.Recurrence.DAILY,
        )
        assert schedule._meta.verbose_name == "Nest Reminder Schedule"
        assert schedule._meta.verbose_name_plural == "Nest Reminder Schedules"
        assert schedule._meta.db_table == "nest_reminder_schedules"
        assert schedule._meta.get_field("reminder").verbose_name == "Nest Reminder"
        assert schedule._meta.get_field("scheduled_time").verbose_name == "Scheduled Time"
        assert schedule._meta.get_field("recurrence").verbose_name == "Recurrence"
