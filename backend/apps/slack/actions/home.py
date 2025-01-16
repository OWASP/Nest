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
    payload = body.get("actions", [])[0]
    value = payload.get("value", "1")

    try:
        page = int(value) if value.isdigit() else 1
        blocks = []

        match action_id:
            case (
                "view_projects_action"
                | "view_projects_action_prev"
                | "view_projects_action_next"
            ):
                details = get_projects(query="", limit=10, page=page)
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
                        for idx, project in enumerate(details["hits"], start=(page - 1) * 10 + 1)
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

                add_pagination_buttons(
                    blocks,
                    page,
                    details["nbPages"],
                    "view_projects_action_prev",
                    "view_projects_action_next",
                )

            case (
                "view_committees_action"
                | "view_committees_action_prev"
                | "view_committees_action_next"
            ):
                details = get_committees(query="", limit=10, page=page)
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
                        for idx, committee in enumerate(details["hits"], start=(page - 1) * 10 + 1)
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

                add_pagination_buttons(
                    blocks,
                    page,
                    details["nbPages"],
                    "view_committees_action_prev",
                    "view_committees_action_next",
                )

            case (
                "view_chapters_action"
                | "view_chapters_action_prev"
                | "view_chapters_action_next"
            ):
                details = get_chapters(query="", limit=10, page=page)
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
                        for idx, chapter in enumerate(details["hits"], start=(page - 1) * 10 + 1)
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

                add_pagination_buttons(
                    blocks,
                    page,
                    details["nbPages"],
                    "view_chapters_action_prev",
                    "view_chapters_action_next",
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


def add_pagination_buttons(blocks, page, total_pages, action_id_prev, action_id_next):
    """Add pagination buttons to the blocks."""
    pagination_buttons = []

    if page > 1:
        pagination_buttons.append(
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Previous"},
                "action_id": action_id_prev,
                "value": str(page - 1),
                "style": "primary",
            }
        )

    if total_pages > page:
        pagination_buttons.append(
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Next"},
                "action_id": action_id_next,
                "value": str(page + 1),
                "style": "primary",
            }
        )

    if pagination_buttons:
        blocks.append(
            {
                "type": "actions",
                "elements": pagination_buttons,
            }
        )


# Register the actions
if SlackConfig.app:
    actions = [
        VIEW_PROJECTS_ACTION,
        VIEW_CHAPTERS_ACTION,
        VIEW_COMMITTEES_ACTION,
        "view_projects_action_prev",
        "view_projects_action_next",
        "view_committees_action_prev",
        "view_committees_action_next",
        "view_chapters_action_prev",
        "view_chapters_action_next",
    ]
    for action in actions:
        SlackConfig.app.action(action)(handle_home_actions)
