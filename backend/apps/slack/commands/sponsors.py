"""Slack bot sponsors command."""

from django.conf import settings

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.utils import get_sponsors_data, get_text

COMMAND = "/sponsors"


def sponsors_handler(ack, command, client):
    """Slack /sponsors command handler.

    Args:
    ----
        ack (function): Function to acknowledge the Slack command.
        command (dict): The Slack command payload.
        client (SlackClient): The Slack client instance for sending messages.

    """
    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    sponsors = get_sponsors_data()
    if not sponsors:
        client.chat_postMessage(
            channel=command["user_id"], text="Failed to get OWASP sponsor data."
        )
        return

    blocks = []
    blocks.append(markdown("*OWASP Sponsors:*"))

    for idx, sponsor in enumerate(sponsors, start=1):
        if sponsor.url:
            block_text = f"*{idx}. <{sponsor.url}|{sponsor.name}>*{NL}"
        else:
            block_text = f"*{idx}. {sponsor.name}*{NL}"

        block_text += f"Member Type: {sponsor.member_type}{NL}"
        block_text += f"{sponsor.description}{NL}"

        blocks.append(markdown(block_text))

    blocks.append({"type": "divider"})
    blocks.append(
        markdown(
            f"* Please visit the <{OWASP_WEBSITE_URL}/supporters|OWASP supporters>"
            f" for more information about the sponsors*{NL}"
            f"{FEEDBACK_CHANNEL_MESSAGE}"
        )
    )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    sponsors_handler = SlackConfig.app.command(COMMAND)(sponsors_handler)
