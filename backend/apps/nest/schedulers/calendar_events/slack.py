"""Slack Scheduler for Nest Calendar Events."""

from apps.nest.schedulers.calendar_events.base import BaseScheduler
from apps.nest.utils.calendar_events import update_reminder_schedule_date
from apps.owasp.models.entity_channel import EntityChannel
from apps.slack.apps import SlackConfig


class SlackScheduler(BaseScheduler):
    """Slack Scheduler Class for Nest Calendar Events."""

    @staticmethod
    def send_message(message: str, channel_id: int):
        """Send message to the specified Slack channel."""
        entity_channel = EntityChannel.objects.get(pk=channel_id)

        if app := SlackConfig.app:
            app.client.chat_postMessage(
                channel=entity_channel.channel.slack_channel_id,
                text=message,
            )

    @staticmethod
    def send_and_delete(message: str, channel_id: int, reminder_schedule_id: int):
        """Send message to the specified channel and delete the reminder."""
        # Import here to avoid circular import issues
        from apps.nest.models.reminder_schedule import ReminderSchedule

        SlackScheduler.send_message(message, channel_id)
        if reminder_schedule := ReminderSchedule.objects.filter(pk=reminder_schedule_id).first():
            reminder_schedule.reminder.delete()

    @staticmethod
    def send_and_update(message: str, channel_id: int, reminder_schedule_id: int):
        """Send message and update the reminder schedule."""
        SlackScheduler.send_message(message, channel_id)
        update_reminder_schedule_date(reminder_schedule_id)
