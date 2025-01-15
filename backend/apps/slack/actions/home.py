"""Slack home actions handler."""

import logging

from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.blocks import get_header, markdown
from apps.slack.common.handlers import (
    EntityPresentation,
    chapters_blocks,
    committees_blocks,
    projects_blocks,
)
from apps.slack.constants import (
    VIEW_CHAPTERS_ACTION,
    VIEW_COMMITTEES_ACTION,
    VIEW_PROJECTS_ACTION,
)

logger = logging.getLogger(__name__)


def handle_home_actions(ack, body, client):
    """Handle actions triggered in the home view."""
    ack()

    action_id = body["actions"][0]["action_id"]
    user_id = body["user"]["id"]

    try:
        home_presentation = EntityPresentation(
            name_truncation=80,
            summary_truncation=200,
            include_feedback=False,
            include_timestamps=False,
            include_metadata=True,
        )

        blocks = []

        match action_id:
            case "view_projects_action":
                blocks = projects_blocks(search_query="", limit=10, presentation=home_presentation)

            case "view_committees_action":
                blocks = committees_blocks(
                    search_query="", limit=10, presentation=home_presentation
                )

            case "view_chapters_action":
                blocks = chapters_blocks(search_query="", limit=10, presentation=home_presentation)

            case _:
                blocks = [markdown("Invalid action, please try again.")]

        new_home_view = {
            "type": "home",
            "blocks": [
                *get_header(),
                *blocks,
            ],
        }

        client.views_publish(user_id=user_id, view=new_home_view)

    except SlackApiError as e:
        logger.exception("Error publishing Home Tab for user %s: %s", user_id, e.response["error"])


# Register the actions
if SlackConfig.app:
    SlackConfig.app.action(VIEW_PROJECTS_ACTION)(handle_home_actions)
    SlackConfig.app.action(VIEW_COMMITTEES_ACTION)(handle_home_actions)
    SlackConfig.app.action(VIEW_CHAPTERS_ACTION)(handle_home_actions)
