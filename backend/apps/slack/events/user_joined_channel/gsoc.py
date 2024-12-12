"""Slack bot user joined #gsoc channel handler."""

from django.conf import settings

from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, OWASP_GSOC_CHANNEL_ID


def handler(event, client, ack):
    """Slack #gsoc new user handler."""
    from apps.slack.common.gsoc import GENERAL_INFORMATION_BLOCKS

    ack()
    if not settings.SLACK_EVENTS_ENABLED or event["channel"] != OWASP_GSOC_CHANNEL_ID:
        return

    user_id = event["user"]
    conversation = client.conversations_open(users=user_id)

    client.chat_postMessage(
        channel=conversation["channel"]["id"],
        blocks=[
            markdown(
                f"Hello <@{user_id}> and welcome to <#{OWASP_GSOC_CHANNEL_ID}> channel!\n"
                "Here's how you can start your journey toward contributing to OWASP projects and "
                "making the most of GSoC:"
            ),
            *GENERAL_INFORMATION_BLOCKS,
            markdown(f"{FEEDBACK_CHANNEL_MESSAGE}"),
        ],
    )


if SlackConfig.app:
    handler = SlackConfig.app.event("member_joined_channel")(handler)
