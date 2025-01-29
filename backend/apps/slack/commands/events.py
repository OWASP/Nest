"""Slack bot events command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown

COMMAND = "/events"


def events_handler(ack, command, client):
    """Slack /events command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    blocks = [
        markdown(f"Please visit <https://owasp.org/events/|OWASP events> page{NL}"),
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    events_handler = SlackConfig.app.command(COMMAND)(events_handler)
