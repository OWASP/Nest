"""Handler for AI-powered Slack functionality."""

from __future__ import annotations

import logging

from apps.slack.blocks import markdown
from apps.slack.utils import format_ai_response_for_slack

logger = logging.getLogger(__name__)


def get_blocks(
    query: str,
    images: list[str] | None = None,
    channel_id: str | None = None,
    *,
    is_app_mention: bool = False,
) -> list[dict]:
    """Get AI response blocks.

    Args:
        query (str): The user's question.
        images (list[str] | None): A list of base64 encoded image data URIs.
        channel_id (str | None): The Slack channel ID where the query originated.
        is_app_mention (bool): Whether this is an explicit app mention.

    Returns:
        list: A list of Slack blocks representing the AI response.

    """
    ai_response = process_ai_query(
        query.strip(), images=images, channel_id=channel_id, is_app_mention=is_app_mention
    )
    return get_response_blocks(ai_response)


def get_response_blocks(response: str | None) -> list[dict]:
    """Get Slack blocks for an already generated AI response.

    Args:
        response (str | None): The AI's generated response.

    Returns:
        list: A list of Slack blocks representing the AI response.

    """
    # Format the AI response for Slack (remove code blocks, fix markdown)
    return [markdown(format_ai_response_for_slack(response))] if response else get_error_blocks()


def process_ai_query(
    query: str,
    images: list[str] | None = None,
    channel_id: str | None = None,
    *,
    is_app_mention: bool = False,
) -> str | None:
    """Process the AI query using CrewAI flow.

    Args:
        query (str): The user's question.
        images (list[str] | None): A list of base64 encoded image data URIs.
        channel_id (str | None): The Slack channel ID where the query originated.
        is_app_mention (bool): Whether this is an explicit app mention.

    Returns:
        str | None: The AI response, None if error occurred or should be skipped.

    """
    try:
        from apps.ai.flows import process_query

        return process_query(
            query, images=images, channel_id=channel_id, is_app_mention=is_app_mention
        )
    except Exception:
        logger.exception("Failed to process AI query")
        return None


def get_error_blocks() -> list[dict]:
    """Get error response blocks.

    Returns:
        list: A list of Slack blocks with error message.

    """
    return [
        markdown(
            "⚠️ Unfortunately, I'm unable to answer your question at this time.\n"
            "Please try again later or contact support if the issue persists."
        )
    ]


def get_default_response() -> str:
    """Get default response for non-OWASP questions.

    Returns:
        str: A default response for non-OWASP questions.

    """
    return "Please ask questions related to OWASP."
