"""Nest content data helpers for Slack commands."""

from __future__ import annotations

import logging
from functools import lru_cache
from urllib.parse import urljoin

import requests
import yaml
from django.core.cache import cache
from lxml import html
from requests.exceptions import RequestException

from apps.common.constants import OWASP_NEWS_URL

logger: logging.Logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 30 * 60  # 30 minutes
NEWS_CACHE_KEY_PREFIX = "slack:news_data"
STAFF_CACHE_KEY = "slack:staff_data"
STAFF_YAML_URL = "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/staff.yml"


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

        cache.set(cache_key, items, timeout=CACHE_TTL_SECONDS)
    except RequestException:
        logger.exception("Unable to fetch OWASP news data", extra={"url": OWASP_NEWS_URL})
        return []
    else:
        return items


def _is_valid_staff_data(data: object) -> bool:
    """Return True when staff YAML parses to a list of dicts with name keys."""
    if not isinstance(data, list):
        return False
    return all(isinstance(person, dict) and "name" in person for person in data)


def get_staff_data(timeout: float | None = 30) -> list | None:
    """Get staff data.

    Args:
        timeout (float, optional): The request timeout in seconds.

    Returns:
        list or None: A sorted list of staff data dictionaries, or None if an error occurs.

    """
    cache_key = f"{STAFF_CACHE_KEY}:{timeout}"
    if (cached := cache.get(cache_key)) is not None:
        return cached

    try:
        response = requests.get(STAFF_YAML_URL, timeout=timeout)
        response.raise_for_status()
        data = yaml.safe_load(response.text)
        if not _is_valid_staff_data(data):
            logger.error(
                "Unable to parse OWASP staff data file",
                extra={"file_path": STAFF_YAML_URL},
            )
            return None

        result = sorted(data, key=lambda person: person["name"])
        cache.set(cache_key, result, timeout=CACHE_TTL_SECONDS)
    except (AttributeError, KeyError, RequestException, TypeError, yaml.YAMLError):
        logger.exception(
            "Unable to parse OWASP staff data file", extra={"file_path": STAFF_YAML_URL}
        )
        return None
    else:
        return result
