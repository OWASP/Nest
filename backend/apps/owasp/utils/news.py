"""News utility functions for OWASP."""

import logging
from functools import lru_cache
from urllib.parse import urljoin

import requests
from lxml import html

from apps.common.constants import OWASP_NEWS_URL

logger = logging.getLogger(__name__)


@lru_cache
def get_news_data(limit: int = 10, timeout: float | None = 30) -> list[dict[str, str]]:
    """Get news data.

    Args:
        limit: The maximum number of news items to fetch.
        timeout: The request timeout in seconds.

    Returns:
        A list of dictionaries containing news data (author, title, and URL).

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
