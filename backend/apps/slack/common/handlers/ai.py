"""Handler for AI-powered Slack functionality."""

from __future__ import annotations

import logging

from apps.slack.blocks import markdown_blocks
from apps.slack.utils import format_ai_response_for_slack

logger = logging.getLogger(__name__)


def get_blocks(
    query: str,
    images: list[str] | None = None,
    channel_id: str | None = None,
    *,
    is_app_mention: bool = False,
) -> list[dict]:
    """Run the AI flow and return Slack section blocks or error blocks."""
    ai_response = process_ai_query(
        query.strip(), images=images, channel_id=channel_id, is_app_mention=is_app_mention
    )

    if ai_response:
        formatted_response = format_ai_response_for_slack(ai_response)
        if not formatted_response.strip():
            return get_error_blocks()
        return markdown_blocks(formatted_response)
    return get_error_blocks()


def process_ai_query(
    query: str,
    images: list[str] | None = None,
    channel_id: str | None = None,
    *,
    is_app_mention: bool = False,
) -> str | None:
    """Return model text or None on failure / bare YES/NO / empty output."""
    try:
        from apps.ai.flows import process_query

        result = process_query(
            query, images=images, channel_id=channel_id, is_app_mention=is_app_mention
        )
    except Exception:
        logger.exception("Failed to process AI query")
        return None

    if result is None:
        return None
    text = str(result)
    stripped = text.strip()
    if not stripped:
        return None
    if stripped.casefold() in {"yes", "no"}:
        logger.info(
            "Ignoring bare YES/NO pipeline output",
            extra={"channel_id": channel_id},
        )
        return None
    return result


def get_error_blocks() -> list[dict]:
    """Return standard unable-to-answer blocks."""
    return markdown_blocks(
        "⚠️ Unfortunately, I'm unable to answer your question at this time.\n"
        "Please try again later or contact support if the issue persists."
    )


def get_default_response() -> str:
    """Prompt for OWASP-only questions."""
    return "Please ask questions related to OWASP."
