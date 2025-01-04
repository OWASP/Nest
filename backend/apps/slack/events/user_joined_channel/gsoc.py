"""Slack bot user joined #gsoc channel handler."""

import logging

from django.conf import settings
from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, NL, OWASP_GSOC_CHANNEL_ID

logger = logging.getLogger(__name__)


def gsoc_handler(event, client, ack):
    """Slack #gsoc new user handler."""
    from apps.slack.common.gsoc import GSOC_GENERAL_INFORMATION_BLOCKS

    ack()
    if not settings.SLACK_EVENTS_ENABLED:
        return

    user_id = event["user"]

    try:
        conversation = client.conversations_open(users=user_id)
    except SlackApiError as e:
        if e.response["error"] == "cannot_dm_bot":
            logger.warning("Error opening conversation with bot user %s", user_id)
            return
        raise

    client.chat_postMessage(
        channel=conversation["channel"]["id"],
        blocks=[
            markdown(
                f"Hello <@{user_id}> and welcome to <#{OWASP_GSOC_CHANNEL_ID}> channel!{NL}"
                "Here's how you can start your journey toward contributing to OWASP projects and "
                "making the most of Google Summer of Code:"
            ),
            *GSOC_GENERAL_INFORMATION_BLOCKS,
            markdown(
                "🎉 We're excited to have you on board, and we can't wait to see the amazing "
                "contributions you'll make! Happy contributing and good luck with your GSoC "
                "journey!"
            ),
            markdown(f"{FEEDBACK_CHANNEL_MESSAGE}"),
        ],
    )


if SlackConfig.app:

    def check_gsoc_handler(event):
        """Check if the event is a member_joined_channel in #gsoc."""
        return event["channel"] == OWASP_GSOC_CHANNEL_ID

    SlackConfig.app.event("member_joined_channel", matchers=[check_gsoc_handler])(gsoc_handler)
