"""Slack app utils."""

import logging
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
