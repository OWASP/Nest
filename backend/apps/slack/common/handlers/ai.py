"""Handler for AI-powered Slack functionality."""

from __future__ import annotations

import logging

from apps.slack.blocks import markdown
from apps.slack.utils import format_ai_response_for_slack

logger = logging.getLogger(__name__)

# Slack allows up to 3001 characters per mrkdwn block; stay under for safety.
MAX_BLOCK_TEXT_LENGTH = 3000


def format_blocks(text: str | None) -> list[dict]:
    """Turn AI response text into Slack section blocks (no LLM calls).

    Splits content so each block stays within Slack mrkdwn size limits.

    Args:
        text (str | None): Raw or model-formatted answer text (None treated as empty).

    Returns:
        list: Section blocks ready for chat.postMessage.

    """
    formatted_response = format_ai_response_for_slack(text or "")

    if not formatted_response.strip():
        return get_error_blocks()

    if len(formatted_response) <= MAX_BLOCK_TEXT_LENGTH:
        return [markdown(formatted_response)]

    blocks: list[dict] = []
    lines = formatted_response.split("\n")
    current_block_text = ""

    for line in lines:
        line_length = len(line)
        current_length = len(current_block_text)

        if line_length > MAX_BLOCK_TEXT_LENGTH:
            if current_block_text.strip():
                blocks.append(markdown(current_block_text.strip()))
                current_block_text = ""
            for i in range(0, line_length, MAX_BLOCK_TEXT_LENGTH):
                chunk = line[i : i + MAX_BLOCK_TEXT_LENGTH]
                if chunk.strip():
                    blocks.append(markdown(chunk.strip()))
            continue

        if current_block_text:
            if current_length + line_length + 1 > MAX_BLOCK_TEXT_LENGTH:
                blocks.append(markdown(current_block_text.strip()))
                current_block_text = line
            else:
                current_block_text += "\n" + line
        else:
            current_block_text = line

    if current_block_text.strip():
        if len(current_block_text) > MAX_BLOCK_TEXT_LENGTH:
            for i in range(0, len(current_block_text), MAX_BLOCK_TEXT_LENGTH):
                chunk = current_block_text[i : i + MAX_BLOCK_TEXT_LENGTH]
                if chunk.strip():
                    blocks.append(markdown(chunk.strip()))
        else:
            blocks.append(markdown(current_block_text.strip()))

    validated_blocks: list[dict] = []
    for block in blocks:
        block_text = block.get("text", {}).get("text", "")
        if len(block_text) > MAX_BLOCK_TEXT_LENGTH:
            for i in range(0, len(block_text), MAX_BLOCK_TEXT_LENGTH):
                chunk = block_text[i : i + MAX_BLOCK_TEXT_LENGTH]
                if chunk.strip():
                    validated_blocks.append(markdown(chunk.strip()))
        else:
            validated_blocks.append(block)

    if not validated_blocks:
        return get_error_blocks()

    return validated_blocks


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

    if ai_response:
        return format_blocks(str(ai_response))
    return get_error_blocks()


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

        result = process_query(
            query, images=images, channel_id=channel_id, is_app_mention=is_app_mention
        )
    except Exception:
        logger.exception(
            "Failed to process AI query",
            extra={
                "query_len": len(query or ""),
                "channel_id": channel_id,
                "is_app_mention": is_app_mention,
            },
        )
        return None
    if result is None:
        return None
    result_str = str(result).strip()
    if result_str.upper() in {"YES", "NO"}:
        logger.error(
            "process_ai_query received Question Detector-style output; treating as failure",
            extra={"query_len": len(query), "channel_id": channel_id},
        )
        return None
    return result_str


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
