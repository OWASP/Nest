"""Slack bot donate command."""

from django.conf import settings

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.template_system.loader import env
from apps.slack.utils import get_text

COMMAND = "/donate"


def donate_handler(ack, command, client):
    """Handle the Slack /donate command.

    Args:
        ack (function): Acknowledge the Slack command request.
        command (dict): The Slack command payload.
        client (slack_sdk.WebClient): The Slack WebClient instance for API calls.

    """
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    template = env.get_template("donate.txt")
    rendered_text = template.render(
        website_url=OWASP_WEBSITE_URL,
        NL=NL,
        SECTION_BREAK="{{ SECTION_BREAK }}",
        DIVIDER="{{ DIVIDER }}",
    )

    blocks = []
    for section in rendered_text.split("{{ SECTION_BREAK }}"):
        cleaned_section = section.strip()
        if cleaned_section == "{{ DIVIDER }}":
            blocks.append({"type": "divider"})
        elif cleaned_section:
            blocks.append(markdown(cleaned_section))

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    donate_handler = SlackConfig.app.command(COMMAND)(donate_handler)
