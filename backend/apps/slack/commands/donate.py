"""Slack bot donate command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown

COMMAND = "/donate"


def donate_handler(ack, command, client):
    """Slack /donate command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    blocks = [
        markdown(
            f"Please visit <https://owasp.org/donate/|donate to the OWASP Foundation> page{NL}"
        ),
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    donate_handler = SlackConfig.app.command(COMMAND)(donate_handler)
