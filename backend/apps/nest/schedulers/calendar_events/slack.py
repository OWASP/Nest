"""Slack Scheduler for Nest Calendar Events."""

from apps.nest.schedulers.calendar_events.base import BaseScheduler
from apps.nest.utils.calendar_events import update_reminder_schedule_date
from apps.slack.apps import SlackConfig


class SlackScheduler(BaseScheduler):
    """Slack Scheduler Class for Nest Calendar Events."""

    @staticmethod
    def send_message(message: str, channel_id: str):
        """Send message to the specified Slack channel."""
        if app := SlackConfig.app:
            app.client.chat_postMessage(
                channel=channel_id,
                text=message,
            )

    @staticmethod
    def send_message_and_update(message: str, channel_id: str, reminder_schedule):
        """Send message and update the reminder schedule."""
        SlackScheduler.send_message(message, channel_id)
        update_reminder_schedule_date(reminder_schedule)
