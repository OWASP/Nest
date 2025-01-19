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


def get_pagination_buttons(page, total_pages, entity_name):
    """Add pagination buttons to the blocks."""
    pagination_buttons = []

    action_id_prev = f"{entity_name}_action_prev"
    action_id_next = f"{entity_name}_action_next"
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

    return pagination_buttons
