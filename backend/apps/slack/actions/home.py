"""Slack home actions handler."""

import logging

from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.blocks import get_header, markdown
from apps.slack.common.handlers import chapters, committees, projects
from apps.slack.common.presentation import EntityPresentation
from apps.slack.constants import (
    VIEW_CHAPTERS_ACTION,
    VIEW_CHAPTERS_ACTION_NEXT,
    VIEW_CHAPTERS_ACTION_PREV,
    VIEW_COMMITTEES_ACTION,
    VIEW_COMMITTEES_ACTION_NEXT,
    VIEW_COMMITTEES_ACTION_PREV,
    VIEW_PROJECTS_ACTION,
    VIEW_PROJECTS_ACTION_NEXT,
    VIEW_PROJECTS_ACTION_PREV,
)

logger = logging.getLogger(__name__)


def handle_home_actions(ack, body, client):
    """Handle actions triggered in the home view."""
    ack()

    action_id = body["actions"][0]["action_id"]
    user_id = body["user"]["id"]
    payload = body.get("actions", [])[0]
    value = payload.get("value", "1")

    try:
        home_presentation = EntityPresentation(
            include_feedback=False,
            include_metadata=True,
            include_pagination=True,
            include_timestamps=False,
            name_truncation=80,
            summary_truncation=200,
        )

        page = int(value) if value.isdigit() else 1

        blocks = []

        match action_id:
            case action if action in {
                VIEW_CHAPTERS_ACTION,
                VIEW_CHAPTERS_ACTION_PREV,
                VIEW_CHAPTERS_ACTION_NEXT,
            }:
                blocks = chapters.get_blocks(page=page, limit=10, presentation=home_presentation)

            case action if action in {
                VIEW_COMMITTEES_ACTION,
                VIEW_COMMITTEES_ACTION_PREV,
                VIEW_COMMITTEES_ACTION_NEXT,
            }:
                blocks = committees.get_blocks(page=page, limit=10, presentation=home_presentation)

            case action if action in {
                VIEW_PROJECTS_ACTION,
                VIEW_PROJECTS_ACTION_PREV,
                VIEW_PROJECTS_ACTION_NEXT,
            }:
                blocks = projects.get_blocks(page=page, limit=10, presentation=home_presentation)
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
    actions = (
        VIEW_CHAPTERS_ACTION_NEXT,
        VIEW_CHAPTERS_ACTION_PREV,
        VIEW_CHAPTERS_ACTION,
        VIEW_COMMITTEES_ACTION_NEXT,
        VIEW_COMMITTEES_ACTION_PREV,
        VIEW_COMMITTEES_ACTION,
        VIEW_PROJECTS_ACTION_NEXT,
        VIEW_PROJECTS_ACTION_PREV,
        VIEW_PROJECTS_ACTION,
    )
    for action in actions:
        SlackConfig.app.action(action)(handle_home_actions)
