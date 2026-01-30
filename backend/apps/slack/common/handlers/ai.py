"""Handler for AI-powered Slack functionality."""

from __future__ import annotations

import logging

from apps.ai.flows import process_query
from apps.slack.blocks import markdown
from apps.slack.utils import format_ai_response_for_slack

logger = logging.getLogger(__name__)


def get_blocks(
    query: str, channel_id: str | None = None, *, is_app_mention: bool = False
) -> list[dict]:
    """Get AI response blocks.

    Args:
        query (str): The user's question.
        channel_id (str | None): The Slack channel ID where the query originated.
        is_app_mention (bool): Whether this is an explicit app mention.

    Returns:
        list: A list of Slack blocks representing the AI response.

    """
    ai_response = process_ai_query(
        query.strip(), channel_id=channel_id, is_app_mention=is_app_mention
    )

    if ai_response:
        return format_blocks(ai_response)
    return get_error_blocks()


def format_blocks(text: str) -> list[dict]:
    """Format AI response text into Slack blocks.

    Args:
        text (str): The AI response text.

    Returns:
        list: A list of Slack blocks.

    """
    # Format the AI response for Slack (remove code blocks, fix markdown)
    formatted_response = format_ai_response_for_slack(text)
    
    # Slack has a limit of 3001 characters per block text
    # Split into multiple blocks if needed
    MAX_BLOCK_TEXT_LENGTH = 3000  # Leave some margin for safety
    
    if len(formatted_response) <= MAX_BLOCK_TEXT_LENGTH:
        return [markdown(formatted_response)]
    
    # Split into multiple blocks
    blocks = []
    # Try to split at newlines to keep content readable
    lines = formatted_response.split("\n")
    current_block_text = ""
    
    for line in lines:
        line_length = len(line)
        current_length = len(current_block_text)
        
        # If a single line is too long, we need to split it by character count
        if line_length > MAX_BLOCK_TEXT_LENGTH:
            # First, save current block if it has content
            if current_block_text.strip():
                blocks.append(markdown(current_block_text.strip()))
                current_block_text = ""
            
            # Split the long line into chunks
            for i in range(0, line_length, MAX_BLOCK_TEXT_LENGTH):
                chunk = line[i:i + MAX_BLOCK_TEXT_LENGTH]
                blocks.append(markdown(chunk))
            continue
        
        # Check if adding this line would exceed the limit
        if current_block_text:
            # Account for newline character
            if current_length + line_length + 1 > MAX_BLOCK_TEXT_LENGTH:
                # Save current block and start a new one
                blocks.append(markdown(current_block_text.strip()))
                current_block_text = line
            else:
                # Add line to current block
                current_block_text += "\n" + line
        else:
            # Start new block
            current_block_text = line
    
    # Add the last block
    if current_block_text.strip():
        # Final safety check - if still too long, split by character count
        if len(current_block_text) > MAX_BLOCK_TEXT_LENGTH:
            for i in range(0, len(current_block_text), MAX_BLOCK_TEXT_LENGTH):
                chunk = current_block_text[i:i + MAX_BLOCK_TEXT_LENGTH]
                if chunk.strip():
                    blocks.append(markdown(chunk.strip()))
        else:
            blocks.append(markdown(current_block_text.strip()))
    
    # Final validation: ensure all blocks are under the limit
    # This is critical because format_links_for_slack might change text length slightly
    validated_blocks = []
    for block in blocks:
        block_text = block.get("text", {}).get("text", "")
        # Double-check the actual text length in the block
        if len(block_text) > MAX_BLOCK_TEXT_LENGTH:
            # Split this block by character count
            for i in range(0, len(block_text), MAX_BLOCK_TEXT_LENGTH):
                chunk = block_text[i:i + MAX_BLOCK_TEXT_LENGTH]
                if chunk.strip():
                    validated_blocks.append(markdown(chunk.strip()))
        else:
            validated_blocks.append(block)
    
    # One more pass to ensure we didn't miss anything
    final_blocks = []
    for block in validated_blocks:
        block_text = block.get("text", {}).get("text", "")
        if len(block_text) > MAX_BLOCK_TEXT_LENGTH:
            for i in range(0, len(block_text), MAX_BLOCK_TEXT_LENGTH):
                chunk = block_text[i:i + MAX_BLOCK_TEXT_LENGTH]
                if chunk.strip():
                    final_blocks.append(markdown(chunk.strip()))
        else:
            final_blocks.append(block)
    
    return final_blocks


def process_ai_query(
    query: str, channel_id: str | None = None, *, is_app_mention: bool = False
) -> str | None:
    """Process the AI query using CrewAI flow.

    Args:
        query (str): The user's question.
        channel_id (str | None): The Slack channel ID where the query originated.
        is_app_mention (bool): Whether this is an explicit app mention.

    Returns:
        str | None: The AI response, None if error occurred or should be skipped.

    """
    try:
        result = process_query(query, channel_id=channel_id, is_app_mention=is_app_mention)
        # Validate result - if it's just "YES" or "NO", something went wrong
        if result:
            result_str = str(result).strip()
            result_upper = result_str.upper()
            if result_upper == "YES" or result_upper == "NO":
                logger.error(
                    "process_ai_query returned Question Detector output",
                    extra={"query": query[:200], "result": result_str},
                )
                return None
        return result
    except Exception as e:
        logger.exception(
            "Failed to process AI query",
            extra={
                "query": query[:200],
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
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
