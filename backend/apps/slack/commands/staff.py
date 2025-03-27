"""Slack bot staff command."""

from django.conf import settings

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.utils import get_staff_data, get_text

COMMAND = "/staff"


def staff_handler(ack, command, client):
    """Slack /staff command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    items = get_staff_data()
    if not items:
        client.chat_postMessage(
            channel=command["user_id"], text="Failed to get OWASP Foundation staff data."
        )
        return

    blocks = []
    blocks.append(markdown("OWASP Foundation Staff:"))
    for idx, item in enumerate(items, start=1):
        blocks.append(
            markdown(
                f"*{idx}. {item['name']}, {item['title']}*{NL}"  # name
                f"_{item['location']}_{NL}"  # title and location
                f"{item['description'] or ''}"  # description
            )
        )
    blocks.append({"type": "divider"})
    blocks.append(
        markdown(
            f"Please visit <{OWASP_WEBSITE_URL}/corporate/|OWASP staff> page "
            f"for more information.{NL}"
        )
    )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    staff_handler = SlackConfig.app.command(COMMAND)(staff_handler)
