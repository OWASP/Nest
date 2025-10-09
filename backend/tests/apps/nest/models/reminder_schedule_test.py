"""Test cases for ReminderSchedule model."""

from django.utils import timezone

from apps.nest.models.reminder import Reminder
from apps.nest.models.reminder_schedule import ReminderSchedule
from apps.owasp.models.entity_channel import EntityChannel
from apps.slack.models.member import Member


class TestReminderScheduleModel:
    """Test cases for ReminderSchedule model."""

    def test_str_representation(self):
        """Test string representation of the ReminderSchedule model."""
        member = Member(slack_user_id="U123456", username="Test User")
        channel = EntityChannel(channel_id=5)
        reminder = Reminder(
            member=member,
            entity_channel=channel,
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
        channel = EntityChannel(channel_id=5)
        reminder = Reminder(
            member=member,
            entity_channel=channel,
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

    def test_cron_expression_property(self):
        """Test cron_expression property of the ReminderSchedule model."""
        member = Member(slack_user_id="U123456", username="Test User")
        channel = EntityChannel(channel_id=5)
        reminder = Reminder(
            member=member,
            entity_channel=channel,
            message="Test reminder",
        )
        date = timezone.make_aware(timezone.datetime(2023, 1, 1, 12, 0, 0))
        schedule = ReminderSchedule(
            reminder=reminder,
            scheduled_time=date,
            recurrence=ReminderSchedule.Recurrence.DAILY,
        )
        assert schedule.cron_expression == "0 12 * * *"
        schedule.recurrence = ReminderSchedule.Recurrence.WEEKLY
        dow = (date.weekday() + 1) % 7  # Convert to cron DOW (0=Sun, 6=Sat)
        assert schedule.cron_expression == f"0 12 * * {dow}"
        schedule.recurrence = ReminderSchedule.Recurrence.MONTHLY
        assert schedule.cron_expression == "0 12 1 * *"
        schedule.recurrence = ReminderSchedule.Recurrence.ONCE
        assert schedule.cron_expression is None
