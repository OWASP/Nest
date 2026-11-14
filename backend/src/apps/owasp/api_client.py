"""Client for the public OWASP website API."""

from __future__ import annotations

import logging
import time
from http import HTTPStatus
from typing import Any

import requests

logger: logging.Logger = logging.getLogger(__name__)

CHAPTERS_URL = "https://owasp.org/api/public/chapters/list"
PROJECTS_URL = "https://owasp.org/api/public/projects/list"


class OwaspApiClient:
    """Read public catalogs from owasp.org."""

    def __init__(
        self,
        *,
        max_pages: int = 10,
        page_limit: int = 1000,
        timeout: tuple[float, float] = (5, 30),
    ) -> None:
        """Create a client for the public website API.

        Args:
            max_pages (int): Maximum pages to read before treating the catalog as failed.
            page_limit (int): Maximum records requested per page.
            timeout (tuple[float, float]): Connect and read timeouts, in seconds.

        """
        self.max_pages = max_pages
        self.page_limit = page_limit
        self.timeout = timeout

    def list_projects(self) -> list[dict[str, Any]] | None:
        """Return every public project.

        Returns:
            list[dict[str, Any]] | None: Project records, or None when the catalog
            could not be read. None is not an empty catalog.

        """
        return self.list_pages(PROJECTS_URL, "projects")

    def list_chapters(self) -> list[dict[str, Any]] | None:
        """Return every public chapter.

        Returns:
            list[dict[str, Any]] | None: Chapter records, or None when the catalog
            could not be read. None is not an empty catalog.

        """
        return self.list_pages(CHAPTERS_URL, "chapters")

    def list_pages(self, url: str, collection: str) -> list[dict[str, Any]] | None:
        """Return every page of a public collection.

        Args:
            url (str): Collection endpoint.
            collection (str): JSON field that holds the page of records.

        Returns:
            list[dict[str, Any]] | None: Collected records, or None when any page fails.

        """
        records: list[dict[str, Any]] = []
        page_offset = 0
        previous_page: list[dict[str, Any]] | None = None
        for _ in range(self.max_pages):
            page = self.fetch_page(url, collection, page_offset)
            if page is None:
                return None
            if page == previous_page:
                logger.warning(
                    "OWASP %s page repeated at offset %s",
                    collection,
                    page_offset,
                )
                return None

            records.extend(page)
            if len(page) < self.page_limit:
                return records
            previous_page = page
            page_offset += self.page_limit

        logger.warning("OWASP %s catalog exceeded %s pages", collection, self.max_pages)
        return None

    def fetch_page(
        self,
        url: str,
        collection: str,
        page_offset: int,
    ) -> list[dict[str, Any]] | None:
        """Return one page, retrying once when the site responds with 429.

        Args:
            url (str): Collection endpoint.
            collection (str): JSON field that holds the page of records.
            page_offset (int): Number of records to skip.

        Returns:
            list[dict[str, Any]] | None: The page, or None when it could not be read.

        """
        response = None
        for attempt in range(2):
            try:
                response = requests.get(
                    url,
                    params={"limit": self.page_limit, "offset": page_offset},
                    timeout=self.timeout,
                )
            except requests.exceptions.RequestException:
                logger.exception(
                    "Couldn't fetch OWASP %s",
                    collection,
                    extra={"offset": page_offset},
                )
                return None

            if response.status_code != HTTPStatus.TOO_MANY_REQUESTS:
                break

            if attempt == 0:
                retry_after = response.headers.get("Retry-After")
                time.sleep(int(retry_after) if retry_after and retry_after.isdigit() else 1)

        if response is None or response.status_code != HTTPStatus.OK:
            status_code = None if response is None else response.status_code
            logger.warning(
                "Unexpected status code %s fetching OWASP %s",
                status_code,
                collection,
                extra={"offset": page_offset},
            )
            return None

        try:
            payload = response.json()
        except ValueError:
            logger.exception(
                "OWASP %s list was not JSON",
                collection,
                extra={"offset": page_offset},
            )
            return None

        page = payload.get(collection) if isinstance(payload, dict) else None
        if not isinstance(page, list) or any(not isinstance(item, dict) for item in page):
            logger.warning("OWASP %s list had an unexpected shape", collection)
            return None

        return page
