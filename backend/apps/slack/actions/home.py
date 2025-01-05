"""Slack home actions handler."""

import logging

from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.blocks import get_header
from apps.slack.constants import (
    NL,
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
        view_title = ""

        match action_id:
            case "view_projects_action":
                details = get_projects(query="", limit=10, page=1)
                view_title = "*Projects*"
                blocks = (
                    [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*<{project['idx_url']}|{project['idx_name']}>*{NL}"
                                    f":bust_in_silhouette: *Contributors:*"
                                    "{project['idx_contributors_count']} "
                                    f":fork_and_knife: *Forks:* {project['idx_forks_count']} "
                                    f":star2: *Stars:* {project['idx_stars_count']}\n"
                                ),
                            },
                        }
                        for project in details["hits"]
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
                view_title = "*Committees*"
                blocks = (
                    [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*<{committee['idx_url']}|{committee['idx_name']}>*\n"
                                    f"{committee['idx_summary']}\n"
                                ),
                            },
                        }
                        for committee in details["hits"]
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
                view_title = "*Chapters*"
                blocks = (
                    [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*<{chapter['idx_url']}|{chapter['idx_name']}>*\n"
                                    f"{chapter['idx_summary']}\n"
                                ),
                            },
                        }
                        for chapter in details["hits"]
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
                view_title = "*Unknown Action*"
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
                {"type": "section", "text": {"type": "mrkdwn", "text": view_title}},
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
