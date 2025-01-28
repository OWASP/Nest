"""Slack bot contact command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown

COMMAND = "/contact"


def contact_handler(ack, command, client):
    """Slack /contact command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    blocks = [
        markdown(f"Please visit <https://owasp.org/contact/|OWASP contact> page{NL}"),
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    contact_handler = SlackConfig.app.command(COMMAND)(contact_handler)
