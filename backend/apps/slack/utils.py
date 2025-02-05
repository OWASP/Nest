"""Slack app utils."""

import logging
import re
from functools import lru_cache
from html import escape as escape_html
from urllib.parse import urljoin

import requests
import yaml
from lxml import html
from requests.exceptions import RequestException

from apps.common.constants import OWASP_NEWS_URL

logger = logging.getLogger(__name__)


def escape(content):
    """Escape HTML content."""
    return escape_html(content, quote=False)


@lru_cache
def get_gsoc_projects(year):
    """Get GSoC projects."""
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
    """Get news data."""
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
    """Get staff data."""
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


def blocks_to_text(blocks):
    """Convert Slack blocks to plain text, including handling Slack links."""
    text = ""

    for block in blocks:
        if block.get("type") == "section":
            if "text" in block and block["text"].get("type") == "mrkdwn":
                text += _process_mrkdwn(block["text"]["text"]) + "\n"
            elif "fields" in block:
                for field in block["fields"]:
                    if field.get("type") == "mrkdwn":
                        text += _process_mrkdwn(field["text"]) + "\n"
        elif block.get("type") == "divider":
            text += "---\n"
        elif block.get("type") == "context":
            for element in block["elements"]:
                if element.get("type") == "mrkdwn":
                    text += _process_mrkdwn(element["text"]) + "\n"
        elif block.get("type") == "actions":
            for element in block["elements"]:
                if element.get("type") == "button":
                    text += _process_mrkdwn(element["text"]["text"]) + "\n"
        elif block.get("type") == "image":
            text += f"Image: {block.get('image_url', '')}\n"
        elif (
            block.get("type") == "header"
            and "text" in block
            and block["text"].get("type") == "plain_text"
        ):
            text += block["text"]["text"] + "\n"
    return text.strip()


def _process_mrkdwn(text):
    """Process mrkdwn text, including Slack links and stars."""
    slack_link_pattern = re.compile(r"<(https?://[^|]+)\|([^>]+)>")
    return slack_link_pattern.sub(r"\2 (\1)", text).replace("*", "")
