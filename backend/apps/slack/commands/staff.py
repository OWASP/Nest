"""Slack bot staff command."""

from django.conf import settings

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import divider, markdown
from apps.slack.constants import NEST_BOT_NAME, OWASP_PROJECT_NEST_CHANNEL_ID
from apps.slack.template_system.loader import env
from apps.slack.utils import get_staff_data, get_text

COMMAND = "/staff"


def staff_handler(ack, command, client):
    """Handle the Slack /staff command.

    Args:
        ack (function): Acknowledge the Slack command request.
        command (dict): The Slack command payload.
        client (slack_sdk.WebClient): The Slack WebClient instance for API calls.

    """
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    items = get_staff_data()
    template = env.get_template("staff.txt")

    if not items:
        rendered_text = template.render(has_staff=False, NL=NL)
        blocks = [markdown(rendered_text.strip())]
    else:
        blocks = []

        title_text = template.render(mode="title", NL=NL).strip()
        blocks.append(markdown(title_text))

        for idx, item in enumerate(items, start=1):
            staff_text = template.render(mode="staff", idx=idx, item=item, NL=NL).strip()
            blocks.append(markdown(staff_text))

        footer_text = template.render(
            mode="footer",
            website_url=OWASP_WEBSITE_URL,
            feedback_channel=OWASP_PROJECT_NEST_CHANNEL_ID,
            nest_bot_name=NEST_BOT_NAME,
            NL=NL,
        ).strip()
        blocks.append(divider())
        blocks.append(markdown(footer_text))

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    staff_handler = SlackConfig.app.command(COMMAND)(staff_handler)
