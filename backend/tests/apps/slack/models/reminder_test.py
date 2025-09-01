"""Test cases for Reminder model."""

from apps.slack.models.member import Member
from apps.slack.models.reminder import Reminder


class TestReminderModel:
    """Reminder model test cases."""

    def test_str_representation(self):
        """Test string representation of the Reminder model."""
        member = Member(slack_user_id="U123456", username="Test User")
        reminder = Reminder(
            member=member,
            channel_id="C123456",
            message="Test reminder",
            remind_at="2023-01-01T12:00:00Z",
            periodic=False,
        )
        assert (
            str(reminder)
            == f"Reminder for {member} in channel: C123456: Test reminder at 2023-01-01T12:00:00Z"
        )

    def test_verbose_names(self):
        """Test verbose names of the Reminder model."""
        reminder = Reminder(
            member=Member(slack_user_id="U123456", username="Test User"),
            channel_id="C123456",
            message="Test reminder",
            remind_at="2023-01-01T12:00:00Z",
            periodic=False,
        )
        assert reminder._meta.verbose_name == "Slack Reminder"
        assert reminder._meta.verbose_name_plural == "Slack Reminders"
        assert reminder._meta.db_table == "slack_reminders"
        assert reminder._meta.get_field("member").verbose_name == "Slack Member"
        assert reminder._meta.get_field("channel_id").verbose_name == "Channel ID"
        assert reminder._meta.get_field("message").verbose_name == "Reminder Message"
        assert reminder._meta.get_field("remind_at").verbose_name == "Reminder Time"
        assert reminder._meta.get_field("periodic").verbose_name == "Is Periodic"
