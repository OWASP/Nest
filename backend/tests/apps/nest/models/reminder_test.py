"""Test cases for Reminder model."""

from apps.nest.models.reminder import Reminder
from apps.slack.models.member import Member
from apps.owasp.models.entity_channel import EntityChannel


class TestReminderModel:
    """Reminder model test cases."""

    def test_str_representation(self):
        """Test string representation of the Reminder model."""
        member = Member(slack_user_id="U123456", username="Test User")
        channel = EntityChannel(channel_id=5)
        reminder = Reminder(
            member=member,
            entity_channel=channel,
            message="Test reminder",
        )
        assert str(reminder) == f"Reminder for {member} in channel: {channel}: Test reminder"

    def test_verbose_names(self):
        """Test verbose names of the Reminder model."""
        channel = EntityChannel(channel_id=5)
        reminder = Reminder(
            member=Member(slack_user_id="U123456", username="Test User"),
            entity_channel=channel,
            message="Test reminder",
        )
        assert reminder._meta.verbose_name == "Nest Reminder"
        assert reminder._meta.verbose_name_plural == "Nest Reminders"
        assert reminder._meta.db_table == "nest_reminders"
        assert reminder._meta.get_field("member").verbose_name == "Slack Member"
        assert reminder._meta.get_field("entity_channel").verbose_name == "Channel"
        assert reminder._meta.get_field("message").verbose_name == "Reminder Message"
