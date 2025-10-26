"""Slack app utils."""

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


def escape(content) -> str:
    """Escape HTML content.

    Args:
        content (str): The HTML content to escape.

    Returns:
        str: The escaped HTML content.

    """
    return escape_html(content, quote=False)


@lru_cache
def get_gsoc_projects(year: int) -> list:
    """Get GSoC projects.

    Args:
        year (int): The year for which to fetch GSoC projects.

    Returns:
        list: A list of GSoC projects with their attributes.

    """
    from apps.owasp.index.search.project import get_projects

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
        timeout (int, optional): The request timeout in seconds.

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
        timeout (int, optional): The request timeout in seconds.

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
    from apps.owasp.models.sponsor import Sponsor

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
    from apps.owasp.models.post import Post

    try:
        return Post.recent_posts()[:limit]
    except Exception as e:
        logger.exception("Failed to fetch posts data via database", extra={"error": str(e)})
        return None


def _process_section_block(block: dict) -> str | None:
    """Process a section block and extract text content.

    Args:
        block (dict): A Slack section block.

    Returns:
        str or None: The extracted text content, or None if no text found.

    """
    if "text" in block and block["text"].get("type") == "mrkdwn":
        return strip_markdown(block["text"]["text"])

    if "fields" in block:
        return NL.join(
            strip_markdown(field["text"])
            for field in block["fields"]
            if field.get("type") == "mrkdwn"
        )

    return None


def _process_context_block(block: dict) -> str:
    """Process a context block and extract text content.

    Args:
        block (dict): A Slack context block.

    Returns:
        str: The extracted text content from all markdown elements.

    """
    return NL.join(
        strip_markdown(element["text"])
        for element in block["elements"]
        if element.get("type") == "mrkdwn"
    )


def _process_actions_block(block: dict) -> str:
    """Process an actions block and extract button text.

    Args:
        block (dict): A Slack actions block.

    Returns:
        str: The extracted text content from all button elements.

    """
    return NL.join(
        strip_markdown(element["text"]["text"])
        for element in block["elements"]
        if element.get("type") == "button"
    )


def _process_header_block(block: dict) -> str | None:
    """Process a header block and extract text content.

    Args:
        block (dict): A Slack header block.

    Returns:
        str or None: The extracted text content, or None if no text found.

    """
    if "text" in block and block["text"].get("type") == "plain_text":
        return block["text"]["text"]

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
                if section_text := _process_section_block(block):
                    text.append(section_text)
            case "divider":
                text.append("---")
            case "context":
                text.append(_process_context_block(block))
            case "actions":
                text.append(_process_actions_block(block))
            # TODO(arkid15r): consider removing this.
            case "image":
                text.append(f"Image: {block.get('image_url', '')}")
            case "header":
                if header_text := _process_header_block(block):
                    text.append(header_text)

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
