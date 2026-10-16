"""Helpers for syncing OWASP website data."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Literal
from urllib.parse import unquote, urlparse

import requests
from lxml import etree, html
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

if TYPE_CHECKING:
    from lxml.html import HtmlElement

    from apps.owasp.models.common import RepositoryBasedEntityModel

logger: logging.Logger = logging.getLogger(__name__)

HEADER_FOOTER_NAV_TAGS = frozenset({"footer", "header", "nav"})
LEADER_SECTION_NAMES = frozenset({"Chapter Leaders", "Project Leaders"})
MAX_RETRIES = 3
TIMEOUT = 5, 10


class OwaspSync:
    """Read an OWASP website page during sync."""

    @staticmethod
    def apply_leaders(
        entity: RepositoryBasedEntityModel,
        leaders: dict[str, str | None],
    ) -> None:
        """Store leaders found during sync.

        Stored leaders stay as they are when ``leaders`` is empty.

        Args:
            entity (RepositoryBasedEntityModel): Project, chapter, or committee to update.
            leaders (dict[str, str | None]): Leader name to email from the page.

        """
        if not leaders:
            logger.debug("No leaders found on the page; leaving stored leaders unchanged")
            return

        entity.leaders_raw = list(leaders)
        entity.sync_leaders(leaders)

    @staticmethod
    def email_from_mailto(href: str) -> str | None:
        """Return the address from a mailto link."""
        address = unquote(href.removeprefix("mailto:")).split("?", 1)[0].strip()
        return address or None

    @staticmethod
    def host_matches(netloc: str, domain: str) -> bool:
        """Return whether a host is the domain or a subdomain of it."""
        host = netloc.lower().split(":", 1)[0]
        return host == domain or host.endswith(f".{domain}")

    @staticmethod
    def in_header_footer_or_nav(element: HtmlElement) -> bool:
        """Return whether an element sits in the site header, footer, or navigation."""
        return any(ancestor.tag in HEADER_FOOTER_NAV_TAGS for ancestor in element.iterancestors())

    @staticmethod
    def leader_section(page_tree: HtmlElement) -> HtmlElement | None:
        """Return the element that contains the leader cards."""
        for heading in page_tree.xpath("//h2|//h3"):
            if OwaspSync.normalized_text(heading) in LEADER_SECTION_NAMES:
                return heading.getparent()
        return None

    @staticmethod
    def normalized_text(element: HtmlElement) -> str:
        """Return collapsed text content."""
        return " ".join(element.text_content().split())

    @staticmethod
    def page_url(kind: Literal["chapter", "committee", "project"], nest_key: str) -> str:
        """Return the public page URL for a project, chapter, or committee.

        Args:
            kind (Literal["chapter", "committee", "project"]): Entity whose page to open.
            nest_key (str): Entity key used in the public URL.

        Returns:
            str: Absolute owasp.org URL.

        """
        paths = {
            "chapter": f"chapters/{nest_key}",
            "committee": f"groups/{nest_key}-committee",
            "project": f"projects/{nest_key}",
        }
        return f"https://owasp.org/{paths[kind]}"

    def __init__(self, url: bytes | str) -> None:
        """Fetch an OWASP website page."""
        self.page_tree = None
        self.is_request_failed = False

        http_adapter = HTTPAdapter(
            max_retries=Retry(
                backoff_factor=1,
                raise_on_status=False,
                status_forcelist=(429, 500, 502, 503, 504),
                total=MAX_RETRIES,
            )
        )
        self.session = requests.Session()
        self.session.mount("http://", http_adapter)  # NOSONAR
        self.session.mount("https://", http_adapter)

        try:
            page_response = self.session.get(url, timeout=TIMEOUT)
        except requests.exceptions.RequestException:
            logger.exception("Request failed", extra={"url": url})
            self.is_request_failed = True
            return

        if page_response.status_code == HTTPStatus.NOT_FOUND:
            return

        if page_response.status_code != HTTPStatus.OK:
            logger.warning("Unexpected status code %s for %s", page_response.status_code, url)
            self.is_request_failed = True
            return

        try:
            self.page_tree = html.fromstring(page_response.content)
        except etree.ParserError:
            self.is_request_failed = True
            return

    def get_leaders(self) -> dict[str, str | None]:
        """Return leader names mapped to email addresses.

        An empty dict means the page has no leader cards. Callers must leave stored
        leaders unchanged in that case.

        Returns:
            dict[str, str | None]: Leader name to email. The email is None when the
            card has a name and no mailto link.

        """
        if self.page_tree is None:
            return {}

        section = self.leader_section(self.page_tree)
        if section is None:
            return {}

        leaders: dict[str, str | None] = {}
        for heading in section.xpath(".//h3|.//h4"):
            name = self.normalized_text(heading)
            if not name or name in LEADER_SECTION_NAMES or name in leaders:
                continue

            email = None
            for href in heading.getparent().xpath(".//a[starts-with(@href, 'mailto:')]/@href"):
                email = self.email_from_mailto(href)
                if email:
                    break
            leaders[name] = email

        return leaders

    def get_urls(self, domain: str | None = None) -> set[str]:
        """Return absolute URLs from the page body.

        Header, footer, and navigation links are skipped. An empty set means the page
        body had no matching links.

        Args:
            domain (str | None): Optional host filter, such as ``github.com``.

        Returns:
            set[str]: Matching absolute http and https URLs.

        """
        if self.page_tree is None:
            return set()

        urls: set[str] = set()
        for anchor in self.page_tree.xpath("//a[@href]"):
            if self.in_header_footer_or_nav(anchor):
                continue

            href = anchor.get("href")
            if not href:
                continue

            parsed = urlparse(href)
            if parsed.scheme not in {"http", "https"}:
                continue

            if domain is not None and not self.host_matches(parsed.netloc, domain):
                continue

            urls.add(href)
        return urls

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
