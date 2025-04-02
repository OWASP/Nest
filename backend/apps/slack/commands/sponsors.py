"""Slack bot sponsors command."""

from django.conf import settings

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import divider, markdown
from apps.slack.constants import NEST_BOT_NAME, OWASP_PROJECT_NEST_CHANNEL_ID
from apps.slack.template_system.loader import env
from apps.slack.utils import get_sponsors_data, get_text

COMMAND = "/sponsors"


def sponsors_handler(ack, command, client):
    """Slack /sponsors command handler.

    Args:
        ack (function): Function to acknowledge the Slack command.
        command (dict): The Slack command payload.
        client (SlackClient): The Slack client instance for sending messages.

    """
    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    sponsors = get_sponsors_data()
    template = env.get_template("sponsors.txt")

    if not sponsors:
        rendered_text = template.render(has_sponsors=False, NL=NL)
        blocks = [markdown(rendered_text.strip())]
    else:
        blocks = []
        title_text = template.render(mode="title", NL=NL).strip()
        blocks.append(markdown(title_text))

        for idx, sponsor in enumerate(sponsors, start=1):
            sponsor_text = template.render(mode="sponsor", idx=idx, sponsor=sponsor, NL=NL).strip()
            blocks.append(markdown(sponsor_text))

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
    sponsors_handler = SlackConfig.app.command(COMMAND)(sponsors_handler)
