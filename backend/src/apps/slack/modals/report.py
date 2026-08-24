"""Content-report modal view builders and state parsers."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from apps.slack.blocks import markdown
from apps.slack.common.text import (
    PREVIEW_LIMIT,
    fit_quoted_mrkdwn,
    preview_text,
    quote_mrkdwn,
    truncate_chars,
)
from apps.slack.enums import ReportSource, ReportType

if TYPE_CHECKING:
    from apps.slack.models.conversation import Conversation
    from apps.slack.models.message import Message

ALREADY_REPORTED_TEXT = "Already reported."
CONSENT_ACTION_ID = "consent"
CONSENT_BLOCK_ID = "consent"
CONSENT_VALUE = "agreed"
CONTENT_PREVIEW_LABEL = "*Content Preview:*\n"
DM_NOT_VISIBLE_TEXT = (
    "NestBot cannot access direct messages or group chats. "
    "Use `Connect to apps -> Report content` on the message instead."
)
FEATURE_OFF_TEXT = "Content reporting is not configured."
INVALID_LINK_TEXT = "That does not look like a Slack message link. Usage: /report <message link>"
METADATA_UNAVAILABLE_TEXT = "Could not verify this conversation. Please try again in a moment."
MISSING_MESSAGE_TEXT = "Could not load the reported message. Please try again."
MODAL_OPEN_FAILED_TEXT = "Could not open the report dialog. Please try again."
# Modal category options are intentionally spam-only for now.
MODAL_REPORT_TYPES: tuple[str, ...] = tuple(ReportType.values)
NOT_VISIBLE_TEXT = (
    "NestBot cannot access that message. Add NestBot to the channel, "
    "or use `Connect to apps -> Report content` on the message."
)
PRIVATE_CHANNEL_TEXT = "Content reporting is not available in private channels."
REPORT_CONTENT_CALLBACK_ID = "report_content"
REPORT_CONTENT_VIEW_CALLBACK_ID = "report_content_submit"
REPORT_TYPE_ACTION_ID = "report_type"
REPORT_TYPE_BLOCK_ID = "report_type"
SELF_REPORT_TEXT = "You cannot report your own message."
SUBMIT_FAILED_TEXT = "Could not submit the report. Please try again."
SUCCESS_TEXT = "Thanks. Your report was submitted to workspace moderators."
USAGE_TEXT = "Usage: /report <message link>"
VALID_SOURCES = frozenset(ReportSource.values)


def alert_text_section(
    conversation: Conversation,
    message_text: str,
    permalink: str,
    *,
    max_len: int,
) -> str | None:
    """Return a labeled message-text section for moderation alerts, or None to omit.

    Public channels with a permalink rely on Slack's link unfurl instead.
    Direct / group messages include as much text as fits in max_len (formatted).
    Other inaccessible contexts use a truncated content preview.
    """
    if permalink and conversation.is_public_channel:
        return None

    body_budget = max_len - len(CONTENT_PREVIEW_LABEL)
    if body_budget <= 0:
        return None

    if conversation.is_im or conversation.is_mpim:
        raw = message_text or ""
    else:
        raw = truncate_chars(message_text or "", PREVIEW_LIMIT)

    quoted = fit_quoted_mrkdwn(raw, body_budget)
    if not quoted:
        return None
    return f"{CONTENT_PREVIEW_LABEL}{quoted}"


def build_error_modal(text: str) -> dict[str, Any]:
    """Build a non-submittable modal that shows an open-path error."""
    return {
        "type": "modal",
        "callback_id": REPORT_CONTENT_VIEW_CALLBACK_ID,
        "title": {"type": "plain_text", "text": "Report Content"},
        "close": {"type": "plain_text", "text": "Close"},
        "blocks": [markdown(text)],
    }


def build_loading_modal() -> dict[str, Any]:
    """Build a temporary modal so trigger_id can be exchanged immediately."""
    return {
        "type": "modal",
        "callback_id": REPORT_CONTENT_VIEW_CALLBACK_ID,
        "title": {"type": "plain_text", "text": "Report Content"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [markdown("_Loading report dialog..._")],
    }


def build_report_modal(
    *,
    message: Message,
    conversation: Conversation,
    response_url: str,
    source: ReportSource | str,
) -> dict[str, Any]:
    """Build the Report content confirmation modal view (spam-only category for now)."""
    author_id = message.raw_data.get("user") if isinstance(message.raw_data, dict) else None
    quoted = preview_text(message.text)
    summary_lines = [f"*Reported From:* {conversation.content_origin(author_id)}"]
    if quoted:
        summary_lines.append(f"*Content Preview:*\n{quote_mrkdwn(quoted)}")
    summary = "\n\n".join(summary_lines)
    spam_option = report_type_option(MODAL_REPORT_TYPES[0])
    blocks: list[dict[str, Any]] = [
        markdown(summary),
        {
            "type": "input",
            "block_id": REPORT_TYPE_BLOCK_ID,
            "optional": False,
            "label": {"type": "plain_text", "text": "Report Category"},
            "element": {
                "type": "static_select",
                "action_id": REPORT_TYPE_ACTION_ID,
                "placeholder": {"type": "plain_text", "text": "Select a Category"},
                "initial_option": spam_option,
                "options": [report_type_option(report_type) for report_type in MODAL_REPORT_TYPES],
            },
        },
        {
            "type": "input",
            "block_id": CONSENT_BLOCK_ID,
            "optional": False,
            "label": {
                "type": "plain_text",
                "text": "Sharing Consent",
            },
            "element": {
                "type": "checkboxes",
                "action_id": CONSENT_ACTION_ID,
                "options": [
                    {
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                "I understand my name and the reported message "
                                "content will be shared with workspace "
                                "moderators to process this report."
                            ),
                        },
                        "value": CONSENT_VALUE,
                    }
                ],
            },
        },
    ]
    return {
        "type": "modal",
        "callback_id": REPORT_CONTENT_VIEW_CALLBACK_ID,
        "private_metadata": encode_metadata(message.pk, response_url, source),
        "title": {"type": "plain_text", "text": "Report Content"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": blocks,
    }


def consent_given(view: dict[str, Any]) -> bool:
    """Return True when the consent checkbox was selected."""
    values = (view.get("state") or {}).get("values") or {}
    block = values.get(CONSENT_BLOCK_ID) or {}
    action = block.get(CONSENT_ACTION_ID) or {}
    selected = action.get("selected_options") or []
    return any(option.get("value") == CONSENT_VALUE for option in selected)


def decode_metadata(raw: str) -> tuple[int, str, str] | None:
    """Decode thin modal private_metadata, or None if invalid."""
    try:
        data = json.loads(raw or "")
        message_db_id = data["message_db_id"]
        response_url = data["response_url"]
        source = data["source"]
    except (KeyError, TypeError, ValueError):
        return None

    # Reject bool/float; JSON ints decode as int (True is a subclass of int).
    if type(message_db_id) is not int or message_db_id <= 0:
        return None
    if not isinstance(response_url, str) or not response_url:
        return None
    if not isinstance(source, str) or source not in VALID_SOURCES:
        return None
    return message_db_id, response_url, source


def encode_metadata(message_db_id: int, response_url: str, source: ReportSource | str) -> str:
    """Encode thin modal private_metadata."""
    return json.dumps(
        {
            "message_db_id": message_db_id,
            "response_url": response_url,
            "source": str(source),
        }
    )


def get_inaccessible_message_error(
    channel_id: str,
    conversation: Conversation | None = None,
) -> str:
    """Return the error when NestBot cannot load a message for /report."""
    if conversation is not None and (conversation.is_im or conversation.is_mpim):
        return DM_NOT_VISIBLE_TEXT
    # D... = IM; G... = MPIM / legacy group - NestBot cannot join these for users.
    if channel_id.startswith(("D", "G")):
        return DM_NOT_VISIBLE_TEXT
    return NOT_VISIBLE_TEXT


def moderator_inaccessibility_note(conversation: Conversation) -> str | None:
    """Return the moderator note for conversations they typically cannot open."""
    if conversation.is_im:
        kind = "direct message"
    elif conversation.is_mpim:
        kind = "group chat"
    else:
        return None
    return (
        "Note: Message contents may not be available for review because this is a "
        f"{kind}. Use the reported content link for reference and the content "
        "preview for context."
    )


def report_type_option(report_type: str) -> dict[str, Any]:
    """Return a Slack static_select option for a report category value."""
    return {
        "text": {"type": "plain_text", "text": ReportType(report_type).label},
        "value": report_type,
    }


def selected_report_type(view: dict[str, Any]) -> str | None:
    """Return the selected modal report category, or None if missing/invalid."""
    values = (view.get("state") or {}).get("values") or {}
    block = values.get(REPORT_TYPE_BLOCK_ID) or {}
    action = block.get(REPORT_TYPE_ACTION_ID) or {}
    option = action.get("selected_option") or {}
    value = option.get("value")
    allowed = set(MODAL_REPORT_TYPES)
    if not isinstance(value, str) or value not in allowed:
        return None
    return value
