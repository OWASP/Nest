"""Dependency-free Slack text formatting helpers."""

from __future__ import annotations

import re
import unicodedata
from html import escape as escape_html
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

NL = "\n"
PREVIEW_LIMIT = 500
# Leave headroom for other alert sections inside one Slack section block (~3000 max).
ALERT_MESSAGE_TEXT_LIMIT = 2500
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


def get_text(blocks: Sequence[Mapping[str, Any]]) -> str:
    """Convert blocks to plain text.

    Args:
        blocks: A sequence of Slack block elements (list or tuple of dicts).

    Returns:
        str: The plain text representation of the blocks.

    """
    text = []

    for block in blocks:
        match block.get("type"):
            case "section":
                if "text" in block and block["text"].get("type") in ("mrkdwn", "plain_text"):
                    section_text = block["text"]["text"]
                    if block["text"].get("type") == "mrkdwn":
                        text.append(strip_markdown(section_text))
                    else:
                        text.append(section_text)
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
    return sanitize_mrkdwn(truncate_chars(text or "", limit))


def quote_mrkdwn(text: str) -> str:
    """Prefix each line so Slack renders a multiline blockquote."""
    if not text:
        return ""
    return "\n".join(f">{line}" for line in text.split("\n"))


def visible_len(text: str) -> int:
    """Count characters the way Django Truncator.chars does (skip combining marks)."""
    return sum(1 for char in text if not unicodedata.combining(char))


def prefix_by_visible_len(text: str, limit: int) -> str:
    """Return a prefix with at most limit non-combining characters."""
    if limit <= 0:
        return ""
    visible = 0
    end = 0
    for index, char in enumerate(text):
        if unicodedata.combining(char):
            end = index + 1
            continue
        if visible >= limit:
            break
        visible += 1
        end = index + 1
    return text[:end]


def truncate_chars(text: str, limit: int, ellipsis: str = "...") -> str:
    """Truncate text to at most limit visible characters, dependency-free.

    Mirrors Django Truncator.chars for NFC normalization and combining marks, and
    caps the ellipsis so the result never exceeds the requested limit.
    """
    if limit <= 0:
        return ""

    text = unicodedata.normalize("NFC", text)
    if visible_len(text) <= limit:
        return text

    ellipsis = prefix_by_visible_len(ellipsis, limit)
    keep = limit - visible_len(ellipsis)
    return f"{prefix_by_visible_len(text, keep)}{ellipsis}"


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
