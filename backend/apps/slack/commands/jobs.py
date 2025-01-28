"""Slack bot jobs command."""

from django.conf import settings

from apps.common.constants import NL, OWASP_WEBSITE_URL
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
        markdown(
            "This Slack channel contains community"
            "-driven posts about job opportunities, "
            "professional networking, and career advice"
            " in cybersecurity and related fields. "
            "\n\n⚠️ *Important Disclaimer:* This is *NOT* an"
            " official OWASP channel, and its contents "
            "have *NOT* been endorsed, reviewed, or approved by"
            " OWASP. The information shared here is "
            "community-generated and not connected to the "
            f"<{OWASP_WEBSITE_URL}/careers/|official OWASP Careers page>. "
            "For official OWASP resources, visit the OWASP website."
            f"please visit the <{OWASP_WEBSITE_URL}/|OWASP website>."
        ),
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    jobs_handler = SlackConfig.app.command(COMMAND)(jobs_handler)
