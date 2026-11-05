"""Formatting and Slack content helpers."""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from html import escape as escape_html
from typing import TYPE_CHECKING
from urllib.parse import urljoin

if TYPE_CHECKING:  # pragma: no cover
    from django.db.models import QuerySet

import requests
import yaml
from lxml import html
from requests.exceptions import RequestException

from apps.common.constants import NL, OWASP_NEWS_URL

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


def format_ai_response_for_slack(text: str) -> str:
    """Format AI response text for Slack by removing code blocks and fixing markdown.

    Args:
        text (str): The AI response text that may contain markdown code blocks.

    Returns:
        str: Text formatted for Slack mrkdwn format.

    """
    if not text:
        return text

    # Strip leading/trailing whitespace
    text = text.strip()

    # Check if the entire response is wrapped in code blocks
    # Pattern: starts with ``` and ends with ```
    if text.startswith("```") and text.endswith("```"):
        # Extract content from code block wrapper
        # Remove first ``` and optional language identifier
        text = re.sub(r"^```[\w]*\n?", "", text, count=1)
        # Remove trailing ```
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()

    # Remove markdown code blocks (```language\ncode\n```) and convert to plain text
    # This regex matches code blocks with optional language identifier
    # Pattern: ```optional_lang\ncontent\n```
    code_block_pattern = re.compile(r"```[\w]*\n(.*?)```", re.DOTALL)

    def replace_code_block(match):
        # Convert code block content to plain text
        # This prevents Slack from rendering it as a code block
        # Preserve Slack channel links that might be inside code blocks
        return match.group(1).strip()

    text = code_block_pattern.sub(replace_code_block, text)

    # Remove any remaining triple backticks that might have been missed
    # (handles edge cases where regex didn't match)
    # Also handle cases where backticks are on separate lines
    text = re.sub(r"```+", "", text)

    # Remove single backticks that might wrap inline code
    # But preserve Slack channel/user links (format: <#...|...> or <@...|...>)
    # Pattern: `text` but not part of Slack link syntax
    text = re.sub(r"`([^`<]+)`", r"\1", text)

    # Preserve Slack channel links (format: <#channel_id|channel_name>)
    # These should not be modified by format_links_for_slack
    # Convert markdown links to Slack format (but preserve existing Slack links)
    return format_links_for_slack(text)


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


@lru_cache
def get_gsoc_projects(year: int) -> list:
    """Get GSoC projects.

    Args:
        year (int): The year for which to fetch GSoC projects.

    Returns:
        list: A list of GSoC projects with their attributes.

    """
    from apps.owasp.index.search.project import get_projects  # noqa: PLC0415

    return get_projects(
        attributes=["idx_name", "idx_url"],
        query=f"gsoc{year}",
        searchable_attributes=[
            "idx_custom_tags",
            "idx_languages",
            "idx_tags",
            "idx_topics",
        ],
    )["hits"]


@lru_cache
def get_news_data(limit: int = 10, timeout: float | None = 30) -> list[dict[str, str]]:
    """Get news data.

    Args:
        limit (int, optional): The maximum number of news items to fetch.
        timeout (float, optional): The request timeout in seconds.

    Returns:
        list: A list of dictionaries containing news data (author, title, and URL).

    """
    response = requests.get(OWASP_NEWS_URL, timeout=timeout)
    tree = html.fromstring(response.content)
    h2_tags = tree.xpath("//h2")

    items_total = 0
    items = []
    for h2 in h2_tags:
        if anchor := h2.xpath(".//a[@href]"):
            author_tag = h2.xpath("./following-sibling::p[@class='author']")
            items.append(
                {
                    "author": author_tag[0].text_content().strip() if author_tag else "",
                    "title": anchor[0].text_content().strip(),
                    "url": urljoin(OWASP_NEWS_URL, anchor[0].get("href")),
                }
            )
            items_total += 1

        if items_total == limit:
            break

    return items


@lru_cache
def get_staff_data(timeout: float | None = 30) -> list | None:
    """Get staff data.

    Args:
        timeout (float, optional): The request timeout in seconds.

    Returns:
        list or None: A sorted list of staff data dictionaries, or None if an error occurs.

    """
    file_path = "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/staff.yml"
    try:
        return sorted(
            yaml.safe_load(
                requests.get(
                    file_path,
                    timeout=timeout,
                ).text
            ),
            key=lambda p: p["name"],
        )
    except (RequestException, yaml.scanner.ScannerError):
        logger.exception("Unable to parse OWASP staff data file", extra={"file_path": file_path})
        return None


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
