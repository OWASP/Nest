"""Slack Task Functions for Nest Schedulers."""

from apps.slack.apps import SlackConfig


def send_message(message: str, channel_id: str):
    """Send the Slack message."""
    if app := SlackConfig.app:
        app.client.chat_postMessage(
            channel=channel_id,
            text=message,
        )
