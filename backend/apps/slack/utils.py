"""Slack app utils."""

import logging
import re
from functools import lru_cache
from html import escape as escape_html
from urllib.parse import urljoin

import requests
import yaml
from django.utils import timezone
from lxml import html
from requests.exceptions import RequestException

from apps.common.constants import NL, OWASP_NEWS_URL

logger = logging.getLogger(__name__)


def escape(content):
    """Escape HTML content.

    Args:
        content (str): The HTML content to escape.

    Returns:
        str: The escaped HTML content.

    """
    return escape_html(content, quote=False)


@lru_cache
def get_gsoc_projects(year):
    """Get GSoC projects.

    Args:
        year (int): The year for which to fetch GSoC projects.

    Returns:
        list: A list of GSoC projects with their attributes.

    """
    from apps.owasp.api.search.project import get_projects

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
def get_news_data(limit=10, timeout=30):
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
def get_staff_data(timeout=30):
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


def get_events_data():
    """Get events data.

    Returns
        QuerySet or None: A queryset of upcoming events.

    """
    from apps.owasp.models.event import Event

    try:
        return Event.objects.filter(start_date__gte=timezone.now()).order_by("start_date")
    except Exception as e:
        logger.exception("Failed to fetch events data via database", extra={"error": str(e)})
        return None


def get_sponsors_data(limit=10):
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
def get_posts_data(limit=5):
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


def get_text(blocks):
    """Convert blocks to plain text.

    Args:
        blocks (list): A list of Slack block elements.

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


def strip_markdown(text):
    """Strip markdown formatting.

    Args:
        text (str): The text with markdown formatting.

    Returns:
        str: The text with markdown formatting removed.

    """
    slack_link_pattern = re.compile(r"<(https?://[^|]+)\|([^>]+)>")
    return slack_link_pattern.sub(r"\2 (\1)", text).replace("*", "")
