"""News utility functions for OWASP."""

import logging
from urllib.parse import urljoin

import requests
from django.core.cache import cache
from lxml import etree, html
from requests.exceptions import RequestException

from apps.common.constants import OWASP_NEWS_URL

logger = logging.getLogger(__name__)
CACHE_TTL_SECONDS = 30 * 60
NEWS_CACHE_KEY_PREFIX = "slack:news_data"


def get_news_data(limit: int = 10, timeout: float | None = 30) -> list[dict[str, str]]:
    """Get news data.

    Args:
        limit (int, optional): The maximum number of news items to fetch.
        timeout (float, optional): The request timeout in seconds.

    Returns:
        list: A list of dictionaries containing news data (author, title, and URL).

    """
    if limit <= 0:
        return []

    cache_key = f"{NEWS_CACHE_KEY_PREFIX}:{limit}:{timeout}"
    if (cached := cache.get(cache_key)) is not None:
        return cached

    try:
        response = requests.get(OWASP_NEWS_URL, timeout=timeout)
        response.raise_for_status()
        if not response.content:
            return []
        tree = html.fromstring(response.content)
        h2_tags = tree.xpath("//h2")

        items_total = 0
        items = []
        for h2 in h2_tags:
            if anchor := h2.xpath(".//a[@href]"):
                author_tag = []
                for sibling in h2.itersiblings():
                    if sibling.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                        break
                    if sibling.tag == "p" and "author" in sibling.get("class", "").split():
                        author_tag = [sibling]
                        break
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

        cache.set(cache_key, items, timeout=CACHE_TTL_SECONDS)
    except etree.ParserError:
        logger.exception("Unable to parse OWASP news HTML", extra={"url": OWASP_NEWS_URL})
        return []
    except RequestException:
        logger.exception("Unable to fetch OWASP news data", extra={"url": OWASP_NEWS_URL})
        return []
    else:
        return items
