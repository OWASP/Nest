"""Slack bot donate command."""

from django.conf import settings

from apps.common.constants import NL
from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown

COMMAND = "/donate"


def donate_handler(ack, command, client):
    """Slack /donate command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    blocks = [
        markdown(
        "The *OWASP Foundation* is a nonprofit organization committed to improving software security globally. "
        "Donations can be unrestricted, supporting the foundation's mission broadly, or restricted for contributions, allocated to specific projects or chapters. "
        "Donors may receive public acknowledgment for their support, lasting at least one year or until the next major project release. "
        "The foundation also welcomes substantial grants from corporations and major foundations. " 
           
        ),
       {"type": "divider"},
        markdown(
             f"Please Visit <{OWASP_WEBSITE_URL}/donate/| OWASP Foundation> Page to *Donate*.{NL}"
        )
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    donate_handler = SlackConfig.app.command(COMMAND)(donate_handler)
