"""Slack bot jobs command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, OWASP_JOBS_CHANNEL_ID
from apps.slack.template_system.loader import env
from apps.slack.utils import get_text

COMMAND = "/jobs"


def jobs_handler(ack, command, client):
    """Handle the Slack /jobs command.

    Args:
        ack (function): Acknowledge the Slack command request.
        command (dict): The Slack command payload.
        client (slack_sdk.WebClient): The Slack WebClient instance for API calls.

    """
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    template = env.get_template("jobs.txt")
    rendered_text = template.render(
        jobs_channel=OWASP_JOBS_CHANNEL_ID, feedback_message=FEEDBACK_CHANNEL_MESSAGE, NL=NL
    )

    blocks = []
    for section in rendered_text.split("{{ SECTION_BREAK }}"):
        cleaned_section = section.strip()
        if cleaned_section:
            blocks.append(markdown(cleaned_section))

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    jobs_handler = SlackConfig.app.command(COMMAND)(jobs_handler)
