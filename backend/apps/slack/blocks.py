"""Slack blocks."""

from __future__ import annotations

from typing import Any

from apps.slack.utils import format_links_for_slack

DIVIDER = "{{ DIVIDER }}"
SECTION_BREAK = "{{ SECTION_BREAK }}"

SLACK_SECTION_MRKDWN_MAX_CHARS = 3000
SLACK_MAX_BLOCKS_PER_MESSAGE = 50


def _split_mrkdwn_text(text: str, max_chars: int = SLACK_SECTION_MRKDWN_MAX_CHARS) -> list[str]:
    """Split long text into chunks that each fit in one Slack section mrkdwn field."""
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    start = 0
    n = len(text)
    min_break = max_chars // 2
    while start < n:
        end = min(start + max_chars, n)
        if end < n:
            window = text[start:end]
            nl = window.rfind("\n")
            if nl != -1 and nl >= min_break:
                end = start + nl + 1
            else:
                sp = window.rfind(" ")
                if sp != -1 and sp >= min_break:
                    end = start + sp + 1
        chunks.append(text[start:end])
        start = end
    return chunks


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


def markdown_blocks(text: str, *, max_blocks: int = SLACK_MAX_BLOCKS_PER_MESSAGE) -> list[dict]:
    """Section blocks with mrkdwn under Slack length limits (link conversion applied)."""
    effective_cap = max(1, min(max_blocks, SLACK_MAX_BLOCKS_PER_MESSAGE))
    formatted = format_links_for_slack(text)
    parts = _split_mrkdwn_text(formatted)
    if len(parts) > effective_cap:
        parts = parts[:effective_cap]
        suffix = "\n\n_(Message truncated for Slack limits.)_"
        ellipsis = "..."
        tail_budget = len(ellipsis) + len(suffix)
        room_for_prefix = SLACK_SECTION_MRKDWN_MAX_CHARS - tail_budget
        if room_for_prefix < 1:
            parts[-1] = (suffix.strip())[:SLACK_SECTION_MRKDWN_MAX_CHARS]
        elif len(parts[-1]) > room_for_prefix:
            prefix_len = max(0, room_for_prefix)
            parts[-1] = parts[-1][:prefix_len].rstrip() + ellipsis + suffix
        else:
            combined = parts[-1].rstrip() + suffix
            if len(combined) > SLACK_SECTION_MRKDWN_MAX_CHARS:
                room = SLACK_SECTION_MRKDWN_MAX_CHARS - len(suffix)
                parts[-1] = parts[-1][: max(0, room)].rstrip() + suffix
            else:
                parts[-1] = combined

    return [{"type": "section", "text": {"type": "mrkdwn", "text": p}} for p in parts]


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
