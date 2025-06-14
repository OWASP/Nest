"""OWASP scraper."""

from __future__ import annotations

import logging
from http import HTTPStatus
from urllib.parse import urlparse

import requests
from lxml import etree, html
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger: logging.Logger = logging.getLogger(__name__)

MAX_RETRIES = 3
TIMEOUT = 5, 10


class OwaspScraper:
    """OWASP scraper."""

    def __init__(self, url: bytes | str) -> None:
        """Create OWASP site scraper."""
        self.page_tree = None

        http_adapter = HTTPAdapter(
            max_retries=Retry(
                backoff_factor=1,
                raise_on_status=False,
                status_forcelist=(429, 500, 502, 503, 504),
                total=MAX_RETRIES,
            )
        )
        self.session = requests.Session()
        self.session.mount("http://", http_adapter)
        self.session.mount("https://", http_adapter)

        try:
            page_response = self.session.get(url, timeout=TIMEOUT)
        except requests.exceptions.RequestException:
            logger.exception("Request failed", extra={"url": url})
            return

        if page_response.status_code == HTTPStatus.NOT_FOUND:
            return

        try:
            self.page_tree = html.fromstring(page_response.content)
        except etree.ParserError:
            return

    def get_urls(self, domain=None):
        """Return scraped URLs."""
        return set(
            self.page_tree.xpath(f"//div[@class='sidebar']//a[contains(@href, '{domain}')]/@href")
            if domain is not None
            else self.page_tree.xpath("//div[@class='sidebar']//a/@href")
        )

    def verify_url(self, url):
        """Verify URL."""
        location = urlparse(url).netloc.lower()
        if not location:
            return None

        if location.endswith(("linkedin.com", "slack.com", "youtube.com")):
            return url

        try:
            # Check for redirects.
            response = self.session.get(url, allow_redirects=False, timeout=TIMEOUT)
        except requests.exceptions.RequestException:
            logger.exception("Request failed", extra={"url": url})
            return None

        if response.status_code == HTTPStatus.OK:
            return url

        if response.status_code in {
            HTTPStatus.MOVED_PERMANENTLY,  # 301
            HTTPStatus.FOUND,  # 302
            HTTPStatus.SEE_OTHER,  # 303
            HTTPStatus.TEMPORARY_REDIRECT,  # 307
            HTTPStatus.PERMANENT_REDIRECT,  # 308
        }:
            return self.verify_url(response.headers["Location"])

        logger.warning("Couldn't verify URL %s", url)

        return None
