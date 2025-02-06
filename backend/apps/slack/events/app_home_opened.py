"""Slack bot app_home_opened event handler."""

import logging

from django.conf import settings
from slack_sdk.errors import SlackApiError

from apps.common.constants import NL, TAB
from apps.slack.apps import SlackConfig
from apps.slack.blocks import get_header, markdown

logger = logging.getLogger(__name__)


def app_home_opened_handler(event, client, ack):
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
                markdown(
                    f"*Hi <@{user_id}>!*{NL}"
                    "Welcome to the OWASP Slack Community! Here you can connect with other "
                    "members, collaborate on projects, and learn about the latest OWASP news and "
                    f"events.{2*NL}"
                    "I'm OWASP @nestbot, your friendly neighborhood bot. Please use one of the "
                    f"following commands:{NL}"
                    f"{TAB}• /board{NL}"
                    f"{TAB}• /chapters{NL}"
                    f"{TAB}• /committees{NL}"
                    f"{TAB}• /community{NL}"
                    f"{TAB}• /contact{NL}"
                    f"{TAB}• /contribute{NL}"
                    f"{TAB}• /donate{NL}"
                    f"{TAB}• /gsoc{NL}"
                    f"{TAB}• /jobs{NL}"
                    f"{TAB}• /leaders{NL}"
                    f"{TAB}• /news{NL}"
                    f"{TAB}• /owasp{NL}"
                    f"{TAB}• /projects{NL}"
                    f"{TAB}• /sponsors{NL}"
                    f"{TAB}• /staff{NL}"
                    f"{TAB}• /users{NL}"
                ),
            ],
        }

        client.views_publish(user_id=user_id, view=home_view)

    except SlackApiError:
        logger.exception("Error publishing Home Tab for user {user_id}: {e.response['error']}")


if SlackConfig.app:
    app_home_opened_handler = SlackConfig.app.event("app_home_opened")(app_home_opened_handler)
