"""Slack home actions handler."""

import logging

from slack_sdk.errors import SlackApiError

from apps.common.constants import NL
from apps.common.utils import truncate
from apps.slack.apps import SlackConfig
from apps.slack.blocks import get_header
from apps.slack.constants import (
    VIEW_CHAPTERS_ACTION,
    VIEW_COMMITTEES_ACTION,
    VIEW_PROJECTS_ACTION,
)

logger = logging.getLogger(__name__)


def handle_home_actions(ack, body, client):
    """Handle actions triggered for Projects, Committees, and Chapters."""
    from apps.owasp.api.search.chapter import get_chapters
    from apps.owasp.api.search.committee import get_committees
    from apps.owasp.api.search.project import get_projects

    ack()

    action_id = body["actions"][0]["action_id"]
    user_id = body["user"]["id"]

    try:
        blocks = []

        match action_id:
            case "view_projects_action":
                details = get_projects(query="", limit=10, page=1)
                blocks = (
                    [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*<{project['idx_url']}|{idx}. {project['idx_name']}>*{NL}"
                                    f"Contributors: {project['idx_contributors_count']} | "
                                    f"Forks: {project['idx_forks_count']} | "
                                    f"Stars: {project['idx_stars_count']}{NL}"
                                    f"{truncate(project['idx_summary'], 300)}"
                                ),
                            },
                        }
                        for idx, project in enumerate(details["hits"], 1)
                    ]
                    if details["hits"]
                    else [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "No projects found based on your search query.",
                            },
                        }
                    ]
                )

            case "view_committees_action":
                details = get_committees(query="", limit=10, page=1)
                blocks = (
                    [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*<{committee['idx_url']}|{idx}. {committee['idx_name']}>*\n"
                                    f"{truncate(committee['idx_summary'], 300)}{NL}"
                                ),
                            },
                        }
                        for idx, committee in enumerate(details["hits"], 1)
                    ]
                    if details["hits"]
                    else [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "No committees found based on your search query.",
                            },
                        }
                    ]
                )

            case "view_chapters_action":
                details = get_chapters(query="", limit=10, page=1)
                blocks = (
                    [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*<{chapter['idx_url']}|{idx}. {chapter['idx_name']}>*\n"
                                    f"{truncate(chapter['idx_summary'], 300)}{NL}"
                                ),
                            },
                        }
                        for idx, chapter in enumerate(details["hits"], 1)
                    ]
                    if details["hits"]
                    else [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "No chapters found based on your search query.",
                            },
                        }
                    ]
                )

            case _:
                blocks.append(
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": "Invalid action, please try again."},
                    }
                )

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
