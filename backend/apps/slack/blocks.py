"""Slack blocks."""


def divider():
    """Return divider block."""
    return {"type": "divider"}


def markdown(text):
    """Return markdown block."""
    return {
        "type": "section",
        "text": {"type": "mrkdwn", "text": text},
    }


def get_header():
    """Return the header block."""
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
            ],
        },
    ]


def get_pagination_buttons(entity_type, page, total_pages):
    """Get pagination buttons for the blocks."""
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
