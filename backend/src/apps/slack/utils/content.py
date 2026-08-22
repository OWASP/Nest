"""Nest content data helpers for Slack commands."""

from __future__ import annotations

import logging
from functools import lru_cache
from urllib.parse import urljoin

import requests
import yaml
from lxml import html
from requests.exceptions import RequestException

from apps.common.constants import OWASP_NEWS_URL

logger: logging.Logger = logging.getLogger(__name__)


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
