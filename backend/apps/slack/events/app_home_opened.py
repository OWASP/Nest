"""Slack bot app_home_opened event handler."""

import logging

from django.conf import settings
from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.blocks import get_header

logger = logging.getLogger(__name__)


def handler(event, client, ack):
    """Handle the app_home_opened event."""
    ack()

    if not settings.SLACK_EVENTS_ENABLED:
        return

    user_id = event["user"]

    try:
        home_view = {
            "type": "home",
            "blocks": [
                *get_header(),
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🏠 Welcome to NestBot, <@{user_id}>!*",
                    },
                },
            ],
        }

        client.views_publish(user_id=user_id, view=home_view)

    except SlackApiError:
        logger.exception("Error publishing Home Tab for user {user_id}: {e.response['error']}")


if SlackConfig.app:
    # Register the app home opened event handler
    SlackConfig.app.event("app_home_opened")(handler)
