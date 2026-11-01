"""Slack blocks."""

from __future__ import annotations

from typing import Any

from apps.slack.utils import format_links_for_slack

DIVIDER = "{{ DIVIDER }}"
SECTION_BREAK = "{{ SECTION_BREAK }}"


def divider() -> dict[str, str]:
    """Return a divider block.

    Returns
        dict: A Slack block representing a divider.

    """
    return {"type": "divider"}


def markdown(text: str) -> dict:
    """Return a markdown block.

    Args:
        text (str): The markdown text to include in the block.

    Returns:
        dict: A Slack block containing markdown text.

    """
    return {
        "type": "section",
        "text": {"type": "mrkdwn", "text": format_links_for_slack(text)},
    }


def get_header() -> list[dict[str, Any]]:
    """Return the header block.

    Returns
        list: A list of Slack blocks representing the header.

    """
    return [
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Projects",
                        "emoji": True,
                    },
                    "value": "view_projects",
                    "action_id": "view_projects_action",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Chapters",
                        "emoji": True,
                    },
                    "value": "view_chapters",
                    "action_id": "view_chapters_action",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Committees",
                        "emoji": True,
                    },
                    "value": "view_committees",
                    "action_id": "view_committees_action",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Contribute",
                        "emoji": True,
                    },
                    "value": "view_contribute",
                    "action_id": "view_contribute_action",
                },
            ],
        },
    ]


def get_pagination_buttons(entity_type: str, page: int, total_pages: int) -> list[dict[str, Any]]:
    """Get pagination buttons for Slack blocks.

    Args:
        entity_type (str): The type of entity being paginated (e.g., "projects").
        page (int): The current page number.
        total_pages (int): The total number of pages.

    Returns:
        list: A list of Slack blocks representing pagination buttons.

    """
    pagination_buttons = []

    if page > 1:
        pagination_buttons.append(
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Previous"},
                "action_id": f"view_{entity_type}_action_prev",
                "value": str(page - 1),
                "style": "primary",
            }
        )

    if total_pages > page:
        pagination_buttons.append(
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Next"},
                "action_id": f"view_{entity_type}_action_next",
                "value": str(page + 1),
                "style": "primary",
            }
        )

    return pagination_buttons
