"""Content-report modal view builders and state parsers."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from apps.slack.blocks import markdown
from apps.slack.common.text import preview_text
from apps.slack.enums import ReportSource, ReportType

if TYPE_CHECKING:
    from apps.slack.models.conversation import Conversation
    from apps.slack.models.message import Message

REPORT_CONTENT_CALLBACK_ID = "report_content"
REPORT_CONTENT_VIEW_CALLBACK_ID = "report_content_submit"
CONSENT_BLOCK_ID = "consent"
CONSENT_ACTION_ID = "consent"
CONSENT_VALUE = "agreed"
REPORT_TYPE_BLOCK_ID = "report_type"
REPORT_TYPE_ACTION_ID = "report_type"

FEATURE_OFF_TEXT = "Content reporting is not configured."
SELF_REPORT_TEXT = "You cannot report your own message."
ALREADY_REPORTED_TEXT = "Already reported."
SUCCESS_TEXT = "Thanks — your report was submitted to workspace moderators."
MISSING_MESSAGE_TEXT = "Could not load the reported message. Please try again."
USAGE_TEXT = "Usage: /report <message link>"
INVALID_LINK_TEXT = "That does not look like a Slack message link. Usage: /report <message link>"
NOT_VISIBLE_TEXT = (
    "NestBot cannot access that message. Add NestBot to the channel, "
    "or use the Report content message shortcut."
)
MODAL_OPEN_FAILED_TEXT = "Could not open the report dialog. Please try again."
SUBMIT_FAILED_TEXT = "Could not submit the report. Please try again."

VALID_SOURCES = frozenset(ReportSource.values)


def encode_metadata(message_db_id: int, response_url: str, source: ReportSource | str) -> str:
    """Encode thin modal private_metadata."""
    return json.dumps(
        {
            "message_db_id": message_db_id,
            "response_url": response_url,
            "source": str(source),
        }
    )


def decode_metadata(raw: str) -> tuple[int, str, str] | None:
    """Decode thin modal private_metadata, or None if invalid."""
    try:
        data = json.loads(raw or "")
        message_db_id = int(data["message_db_id"])
        response_url = data["response_url"]
        source = data["source"]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None

    if not isinstance(response_url, str) or not response_url:
        return None
    if not isinstance(source, str) or source not in VALID_SOURCES:
        return None
    return message_db_id, response_url, source


def build_report_modal(
    *,
    message: Message,
    conversation: Conversation,
    response_url: str,
    source: ReportSource | str,
) -> dict[str, Any]:
    """Build the Report content confirmation modal view."""
    author_id = message.raw_data.get("user") if isinstance(message.raw_data, dict) else None
    author_line = f" from <@{author_id}>" if author_id else ""
    origin = conversation.content_origin
    quoted = preview_text(message.text)
    preview = (
        f"*Message* ({origin}{author_line}):\n>{quoted}"
        if quoted
        else (f"*Message* ({origin}{author_line}):\n_(no text)_")
    )
    report_type_labels = dict(ReportType.choices)
    default_report_type = ReportType.SPAM
    return {
        "type": "modal",
        "callback_id": REPORT_CONTENT_VIEW_CALLBACK_ID,
        "private_metadata": encode_metadata(message.pk, response_url, source),
        "title": {"type": "plain_text", "text": "Report content"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            markdown(preview),
            {
                "type": "input",
                "block_id": REPORT_TYPE_BLOCK_ID,
                "optional": False,
                "label": {"type": "plain_text", "text": "Report category"},
                "element": {
                    "type": "static_select",
                    "action_id": REPORT_TYPE_ACTION_ID,
                    "placeholder": {"type": "plain_text", "text": "Select a category"},
                    "initial_option": {
                        "text": {
                            "type": "plain_text",
                            "text": report_type_labels[default_report_type],
                        },
                        "value": default_report_type,
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": label},
                            "value": value,
                        }
                        for value, label in ReportType.choices
                    ],
                },
            },
            {
                "type": "input",
                "block_id": CONSENT_BLOCK_ID,
                "optional": False,
                "label": {
                    "type": "plain_text",
                    "text": "Confirm sharing with moderators",
                },
                "element": {
                    "type": "checkboxes",
                    "action_id": CONSENT_ACTION_ID,
                    "options": [
                        {
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    "I understand this message will be shared with "
                                    "workspace moderators to process this report."
                                ),
                            },
                            "value": CONSENT_VALUE,
                        }
                    ],
                },
            },
        ],
    }


def consent_given(view: dict[str, Any]) -> bool:
    """Return True when the consent checkbox was selected."""
    values = (view.get("state") or {}).get("values") or {}
    block = values.get(CONSENT_BLOCK_ID) or {}
    action = block.get(CONSENT_ACTION_ID) or {}
    selected = action.get("selected_options") or []
    return any(option.get("value") == CONSENT_VALUE for option in selected)


def selected_report_type(view: dict[str, Any]) -> str | None:
    """Return the selected report category value, or None if missing/invalid."""
    values = (view.get("state") or {}).get("values") or {}
    block = values.get(REPORT_TYPE_BLOCK_ID) or {}
    action = block.get(REPORT_TYPE_ACTION_ID) or {}
    option = action.get("selected_option") or {}
    value = option.get("value")
    if not isinstance(value, str) or value not in ReportType.values:
        return None
    return value
