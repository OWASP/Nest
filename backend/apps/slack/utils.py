"""Slack app utils."""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from html import escape as escape_html
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:  # pragma: no cover
    from django.db.models import QuerySet


from apps.common.constants import NL

logger: logging.Logger = logging.getLogger(__name__)


def download_file(url: str, token: str) -> bytes | None:
    """Download Slack file.

    Args:
        url (str): The url of the file.
        token (str): The slack bot token.

    Returns:
        bytes or None: The downloaded file content, or None if download failed.

    """
    if not url or not token:
        return None

    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.exception("Failed to download Slack file", extra={"error": str(e)})
        return None

    return response.content


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


SLACK_CHAT_POST_FALLBACK_TEXT_MAX = 40_000


def truncate_for_slack_fallback(
    text: str, max_len: int = SLACK_CHAT_POST_FALLBACK_TEXT_MAX
) -> str:
    """Truncate notification/fallback text for chat.postMessage if needed."""
    if len(text) <= max_len:
        return text
    tail = "\n… _(truncated)_"
    if max_len <= 0:
        return ""
    if max_len <= len(tail):
        return text[:max_len]
    cut = max_len - len(tail)
    return text[:cut].rstrip() + tail


def format_ai_response_for_slack(text: str) -> str:
    """Strip code fences and inline backticks; leave markdown links for block builders."""
    if not text:
        return text

    text = text.strip()

    if text.startswith("```") and text.endswith("```"):
        text = re.sub(r"^```[\w]*\n?", "", text, count=1)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()

    code_block_pattern = re.compile(r"```[\w]*\n(.*?)```", re.DOTALL)

    def replace_code_block(match):
        return match.group(1).strip()

    text = code_block_pattern.sub(replace_code_block, text)
    text = re.sub(r"```+", "", text)
    return re.sub(r"`([^`<]+)`", r"\1", text)


def get_sponsors_data(limit: int = 10) -> QuerySet | None:
    """Get sponsors data.

    Args:
        limit (int, optional): The maximum number of sponsors to fetch.

    Returns:
        QuerySet or None: A queryset of sponsors, or None if an error occurs.

    """
    from apps.owasp.models.sponsor import Sponsor  # noqa: PLC0415

    try:
        return Sponsor.objects.all()[:limit]
    except Exception as e:
        logger.exception("Failed to fetch sponsors data via database", extra={"error": str(e)})
        return None


@lru_cache
def get_posts_data(limit: int = 5) -> QuerySet | None:
    """Get posts data.

    Args:
        limit (int, optional): The maximum number of posts to fetch.

    Returns:
        QuerySet or None: A queryset of recent posts, or None if an error occurs.

    """
    from apps.owasp.models.post import Post  # noqa: PLC0415

    try:
        return Post.recent_posts()[:limit]
    except Exception as e:
        logger.exception("Failed to fetch posts data via database", extra={"error": str(e)})
        return None


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


def strip_markdown(text: str) -> str:
    """Strip markdown formatting.

    Args:
        text (str): The text with markdown formatting.

    Returns:
        str: The text with markdown formatting removed.

    """
    slack_link_pattern = re.compile(r"<(https?://[^|]+)\|([^>]+)>")
    return slack_link_pattern.sub(r"\2 (\1)", text).replace("*", "")
