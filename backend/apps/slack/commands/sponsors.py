"""Slack bot sponsors command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown

COMMAND = "/sponsors"


def sponsors_handler(ack, command, client):
    """Slack /sponsors command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    blocks = [
        markdown(
            f"Please visit <https://owasp.org/supporters/list|current sponsors list> page{NL}"
        ),
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    sponsors_handler = SlackConfig.app.command(COMMAND)(sponsors_handler)
