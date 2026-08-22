"""Dependency-free Slack text formatting helpers."""

from __future__ import annotations

import re
from html import escape as escape_html

NL = "\n"
PREVIEW_LIMIT = 500
SLACK_LINK_PATTERN = re.compile(r"<(https?://[^|]+)\|([^>]+)>")


def escape(content: str) -> str:
    """Escape HTML content.

    Args:
        content (str): The HTML content to escape.

    Returns:
        str: The escaped HTML content.

    """
    return escape_html(content, quote=False)


def format_links_for_slack(text: str) -> str:
    """Convert Markdown links to Slack markdown link format.

    Args:
        text (str): The input text that may include Markdown links.

    Returns:
        str: Text with Markdown links converted to Slack markdown links.

    """
    if not text:
        return text

    markdown_link_pattern = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
    return markdown_link_pattern.sub(r"<\2|\1>", text)


def get_text(blocks: tuple) -> str:
    """Convert blocks to plain text.

    Args:
        blocks (tuple): A tuple of Slack block elements.

    Returns:
        str: The plain text representation of the blocks.

    """
    text = []

    for block in blocks:
        match block.get("type"):
            case "section":
                if "text" in block and block["text"].get("type") == "mrkdwn":
                    text.append(strip_markdown(block["text"]["text"]))
                elif "fields" in block:
                    text.append(
                        NL.join(
                            strip_markdown(field["text"])
                            for field in block["fields"]
                            if field.get("type") == "mrkdwn"
                        )
                    )
            case "divider":
                text.append("---")
            case "context":
                text.append(
                    NL.join(
                        strip_markdown(element["text"])
                        for element in block["elements"]
                        if element.get("type") == "mrkdwn"
                    )
                )
            case "actions":
                text.append(
                    NL.join(
                        strip_markdown(element["text"]["text"])
                        for element in block["elements"]
                        if element.get("type") == "button"
                    )
                )
            # TODO(arkid15r): consider removing this.
            case "image":
                text.append(f"Image: {block.get('image_url', '')}")
            case "header":
                if "text" in block and block["text"].get("type") == "plain_text":
                    text.append(block["text"]["text"])

    return NL.join(text).strip()


def preview_text(text: str, limit: int = PREVIEW_LIMIT) -> str:
    """Return a truncated, sanitized preview for modal and alert embeds."""
    content = text or ""
    if len(content) > limit:
        ellipsis = "..."
        keep = max(limit - len(ellipsis), 0)
        content = f"{content[:keep]}{ellipsis}"
    return sanitize_mrkdwn(content)


def sanitize_mrkdwn(text: str) -> str:
    """Escape characters that break Slack mrkdwn in quoted previews."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("*", "\\*")
        .replace("_", "\\_")
        .replace("~", "\\~")
        .replace("`", "\\`")
    )


def strip_markdown(text: str) -> str:
    """Strip markdown formatting.

    Args:
        text (str): The text with markdown formatting.

    Returns:
        str: The text with markdown formatting removed.

    """
    return SLACK_LINK_PATTERN.sub(r"\2 (\1)", text).replace("*", "")
