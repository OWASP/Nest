"""Slack member joined #gsoc channel handler."""

import logging

from django.conf import settings
from slack_sdk.errors import SlackApiError

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.common.gsoc import GSOC_2025_MILESTONES
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, OWASP_GSOC_CHANNEL_ID
from apps.slack.utils import get_text

logger = logging.getLogger(__name__)


def gsoc_handler(event, client, ack):
    """Slack #gsoc new member handler."""
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

    client.chat_postEphemeral(
        blocks=GSOC_2025_MILESTONES,
        channel=event["channel"],
        user=user_id,
    )

    blocks = [
        markdown(
            f"Hello <@{user_id}> and welcome to <{OWASP_GSOC_CHANNEL_ID}> channel!{NL}"
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
    ]
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    SlackConfig.app.event(
        "member_joined_channel",
        matchers=[lambda event: f"#{event['channel']}" == OWASP_GSOC_CHANNEL_ID],
    )(gsoc_handler)
