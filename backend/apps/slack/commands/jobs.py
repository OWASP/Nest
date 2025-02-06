"""Slack bot jobs command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, OWASP_JOBS_CHANNEL_ID
from apps.slack.utils import get_text

COMMAND = "/jobs"


def jobs_handler(ack, command, client):
    """Slack /jobs command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    blocks = [
        markdown(
            f"Please join <{OWASP_JOBS_CHANNEL_ID}> channel{NL}"
            "This Slack channel shares community-driven job opportunities, networking, "
            "and career advice in cybersecurity and related fields."
        ),
        markdown(
            "⚠️ *Disclaimer: This is not an official OWASP channel and its content is "
            "not endorsed, reviewed, or approved by OWASP*."
        ),
        markdown(f"{FEEDBACK_CHANNEL_MESSAGE}"),
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    jobs_handler = SlackConfig.app.command(COMMAND)(jobs_handler)
