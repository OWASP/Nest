"""Dependency-free Slack text formatting helpers."""

import re
from html import escape as escape_html

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


def strip_markdown(text: str) -> str:
    """Strip markdown formatting.

    Args:
        text (str): The text with markdown formatting.

    Returns:
        str: The text with markdown formatting removed.

    """
    return SLACK_LINK_PATTERN.sub(r"\2 (\1)", text).replace("*", "")
