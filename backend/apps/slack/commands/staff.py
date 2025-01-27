"""Slack bot staff command."""

from django.conf import settings
from requests.exceptions import RequestException

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.constants import OWASP_WEBSITE_URL
from apps.slack.utils import get_staff_data

COMMAND = "/staff"


def staff_handler(ack, command, client):
    """Slack /staff command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    try:
        staff_data = get_staff_data()
    except RequestException:
        client.chat_postMessage(channel=command["user_id"], text="Failed to get staff data.")
        return

    blocks = []
    blocks.append(markdown("Here are the OWASP staff members:"))
    for idx, staff in enumerate(staff_data[:10], start=1):
        blocks.append(
            markdown(
                f"*{idx}.* *Name:* *{staff['name']}*{NL}"
                f"*Title:* _{staff['title']}_{NL}{NL}"
                f"*Description:* {staff['description']}"
            )
        )
    blocks.append({"type": "divider"})
    blocks.append(markdown(f"Please visit <{OWASP_WEBSITE_URL}/corporate/|OWASP staff> page.{NL}"))

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    staff_handler = SlackConfig.app.command(COMMAND)(staff_handler)
