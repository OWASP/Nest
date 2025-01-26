"""Slack bot jobs command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.constants import OWASP_JOBS_CHANNEL_ID

COMMAND = "/jobs"


def jobs_handler(ack, command, client):
    """Slack /jobs command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    blocks = [
        markdown(f"Please join <{OWASP_JOBS_CHANNEL_ID}> channel{NL}"),
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    jobs_handler = SlackConfig.app.command(COMMAND)(jobs_handler)
