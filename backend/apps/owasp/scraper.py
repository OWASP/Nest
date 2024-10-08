"""OWASP scraper."""

import logging
from urllib.parse import urlparse

import requests
from lxml import etree, html
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class OwaspScraper:
    """OWASP scraper."""

    def __init__(self, url):
        """Create OWASP site scraper."""
        self.page_tree = None

        http_adapter = HTTPAdapter(
            max_retries=Retry(
                backoff_factor=1,
                raise_on_status=False,
                status_forcelist=(429, 500, 502, 503, 504),
                total=5,
            )
        )
        self.session = requests.Session()
        self.session.mount("http://", http_adapter)
        self.session.mount("https://", http_adapter)

        try:
            page_response = self.session.get(url, timeout=(30, 60))
        except requests.exceptions.RequestException:
            logger.exception("Request failed", extra={"url": url})
            return

        if page_response.status_code == requests.codes.not_found:
            return

        try:
            self.page_tree = html.fromstring(page_response.content)
        except etree.ParserError:
            return

    def get_urls(self, domain=None):
        """Return GitHub URLs."""
        return set(
            self.page_tree.xpath(f"//div[@class='sidebar']//a[contains(@href, {domain})]/@href")
            if domain
            else self.page_tree.xpath("//div[@class='sidebar']//a/@href")
        )

    def get_leaders(self):
        """Get leaders."""
        leaders_header = self.page_tree.xpath("//div[@class='sidebar']//*[@id='leaders']")
        if leaders_header:
            leaders_ul = leaders_header[0].getnext()
            if leaders_ul is not None and leaders_ul.tag == "ul":
                return sorted(name.strip() for name in leaders_ul.xpath(".//li/a/text()"))

        return []

    def verify_url(self, url):
        """Verify URL."""
        location = urlparse(url).netloc.lower()
        if not location:
            return None

        if location.endswith(("linkedin.com", "youtube.com")):
            return url

        try:
            # Check for redirects.
            response = self.session.get(url, allow_redirects=False, timeout=(30, 60))
        except requests.exceptions.RequestException:
            logger.exception("Request failed", extra={"url": url})
            return None

        if response.status_code == requests.codes.ok:
            return url

        if response.status_code in {
            requests.codes.moved_permanently,  # 301
            requests.codes.found,  # 302
            requests.codes.see_other,  # 303
            requests.codes.temporary_redirect,  # 307
            requests.codes.permanent_redirect,  # 308
        }:
            return self.verify_url(response.headers["Location"])

        logger.warning("Couldn't verify URL %s", url)

        return None
