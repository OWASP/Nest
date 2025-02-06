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

from apps.common.constants import NL, OWASP_NEWS_URL

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


def get_text(blocks):
    """Convert blocks to plain text."""
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
    """Strip markdown formatting."""
    slack_link_pattern = re.compile(r"<(https?://[^|]+)\|([^>]+)>")
    return slack_link_pattern.sub(r"\2 (\1)", text).replace("*", "")
