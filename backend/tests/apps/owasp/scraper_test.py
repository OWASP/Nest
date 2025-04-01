from unittest.mock import MagicMock, patch

import pytest
import requests
from lxml import etree

from apps.owasp.scraper import TIMEOUT, OwaspScraper


class TestOwaspScraper:
    @pytest.fixture()
    def mock_session(self):
        session_mock = MagicMock()
        with patch("requests.Session", return_value=session_mock):
            yield session_mock

    @pytest.fixture()
    def mock_urlparse(self):
        with patch("urllib.parse.urlparse") as mock_parse:
            yield mock_parse

    @pytest.fixture()
    def mock_fromstring(self):
        with patch("lxml.html.fromstring") as mock:
            yield mock

    @pytest.fixture()
    def sample_html(self):
        return b"""
            <div class="sidebar">
                <div id="leaders"></div>
                <ul>
                    <li><a href="https://owasp.org/link1">Leader 1</a></li>
                    <li><a href="https://owasp.org/link2">Leader 2</a></li>
                    <li><a href="https://owasp.org/link3">Leader 3</a></li>
                </ul>
                <a href="https://owasp.org/url1">URL 1</a>
                <a href="https://example.com/url2">URL 2</a>
                <a href="https://owasp.org/url3">URL 3</a>
            </div>
        """

    def test_init_success(self, mock_session, mock_fromstring):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><div class='sidebar'></div></body></html>"
        mock_session.get.return_value = mock_response

        tree_mock = MagicMock()
        mock_fromstring.return_value = tree_mock

        scraper = OwaspScraper("https://example.com")

        mock_session.get.assert_called_once_with("https://example.com", timeout=TIMEOUT)
        assert scraper.page_tree == tree_mock

    def test_init_request_exception(self, mock_session):
        mock_session.get.side_effect = requests.exceptions.RequestException()

        with patch("apps.owasp.scraper.logger") as mock_logger:
            scraper = OwaspScraper("https://example.com")
            mock_logger.exception.assert_called_once()
            assert scraper.page_tree is None

    def test_init_not_found(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_session.get.return_value = mock_response

        scraper = OwaspScraper("https://example.com")

        assert scraper.page_tree is None

    def test_init_parser_error(self, mock_session, mock_fromstring):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"invalid html"
        mock_session.get.return_value = mock_response

        mock_fromstring.side_effect = etree.ParserError("Parser error")

        scraper = OwaspScraper("https://example.com")
        assert scraper.page_tree is None

    def test_get_urls_with_domain(self):
        scraper = OwaspScraper.__new__(OwaspScraper)

        mock_tree = MagicMock()
        mock_tree.xpath.return_value = ["https://github.com/repo1", "https://github.com/repo2"]
        scraper.page_tree = mock_tree

        urls = scraper.get_urls(domain="github.com")

        mock_tree.xpath.assert_called_once_with(
            "//div[@class='sidebar']//a[contains(@href, 'github.com')]/@href"
        )
        assert urls == {"https://github.com/repo1", "https://github.com/repo2"}

    def test_get_urls_without_domain(self):
        scraper = OwaspScraper.__new__(OwaspScraper)

        mock_tree = MagicMock()
        mock_tree.xpath.return_value = ["https://github.com/repo1", "https://example.com/other"]
        scraper.page_tree = mock_tree

        urls = scraper.get_urls()

        mock_tree.xpath.assert_called_once_with("//div[@class='sidebar']//a/@href")
        assert urls == {"https://github.com/repo1", "https://example.com/other"}

    def test_get_leaders(self):
        scraper = OwaspScraper.__new__(OwaspScraper)

        leaders_header = MagicMock()
        next_element = MagicMock()
        next_element.tag = "ul"
        next_element.xpath.return_value = ["Leader One", "Leader Two"]
        leaders_header.getnext.return_value = next_element

        mock_tree = MagicMock()
        mock_tree.xpath.return_value = [leaders_header]
        scraper.page_tree = mock_tree

        leaders = scraper.get_leaders()

        mock_tree.xpath.assert_called_once_with("//div[@class='sidebar']//*[@id='leaders']")
        assert leaders == ["Leader One", "Leader Two"]

    def test_get_leaders_no_leaders(self):
        scraper = OwaspScraper.__new__(OwaspScraper)

        mock_tree = MagicMock()
        mock_tree.xpath.return_value = []
        scraper.page_tree = mock_tree

        leaders = scraper.get_leaders()

        assert leaders == []

    def test_get_leaders_not_ul(self):
        scraper = OwaspScraper.__new__(OwaspScraper)

        header = MagicMock()
        next_el = MagicMock()
        next_el.tag = "div"
        header.getnext.return_value = next_el

        mock_tree = MagicMock()
        mock_tree.xpath.return_value = [header]
        scraper.page_tree = mock_tree

        leaders = scraper.get_leaders()

        assert leaders == []

    def test_verify_url_invalid_url(self, mock_urlparse):
        scraper = OwaspScraper.__new__(OwaspScraper)
        scraper.session = MagicMock()

        parsed_url = MagicMock()
        parsed_url.netloc = ""
        mock_urlparse.return_value = parsed_url

        url = "invalid-url"
        with patch("apps.owasp.scraper.urlparse", mock_urlparse):
            result = scraper.verify_url(url)

        assert result is None
        mock_urlparse.assert_called_once_with(url)

    @pytest.mark.parametrize(
        ("domain", "expected"),
        [
            ("linkedin.com", "https://linkedin.com/profile"),
            ("slack.com", "https://slack.com/channel"),
            ("youtube.com", "https://youtube.com/video"),
        ],
    )
    def test_verify_url_social_media(self, mock_urlparse, domain, expected):
        scraper = OwaspScraper.__new__(OwaspScraper)
        scraper.session = MagicMock()

        url = f"https://{domain}/profile"
        if domain == "slack.com":
            url = "https://slack.com/channel"
        elif domain == "youtube.com":
            url = "https://youtube.com/video"

        parsed_url = MagicMock()
        parsed_url.netloc = domain
        mock_urlparse.return_value = parsed_url

        result = scraper.verify_url(url)

        assert result == expected
        scraper.session.get.assert_not_called()

    def test_verify_url_success(self, mock_urlparse, mock_session):
        scraper = OwaspScraper.__new__(OwaspScraper)
        scraper.session = mock_session

        url = "https://test.com"
        parsed_url = MagicMock()
        parsed_url.netloc = "test.com"
        mock_urlparse.return_value = parsed_url

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response

        result = scraper.verify_url(url)

        mock_session.get.assert_called_once_with(url, allow_redirects=False, timeout=TIMEOUT)
        assert result == url

    def test_verify_url_redirect(self, mock_urlparse, mock_session):
        scraper = OwaspScraper.__new__(OwaspScraper)
        scraper.session = mock_session

        url = "https://test.com"

        def mock_urlparse_side_effect(input_url):
            parsed = MagicMock()
            parsed.netloc = input_url.split("//")[1].split("/")[0]
            return parsed

        mock_urlparse.side_effect = mock_urlparse_side_effect

        response1 = MagicMock()
        response1.status_code = 301
        response1.headers = {"Location": "https://redirect.com"}

        response2 = MagicMock()
        response2.status_code = 200

        mock_session.get.side_effect = [response1, response2]

        with patch.object(scraper, "verify_url", wraps=scraper.verify_url):
            result = scraper.verify_url(url)
            assert result == "https://redirect.com"

    def test_verify_url_request_exception(self, mock_urlparse, mock_session):
        scraper = OwaspScraper.__new__(OwaspScraper)
        scraper.session = mock_session

        mock_session.get.side_effect = requests.exceptions.RequestException()

        parsed_url = MagicMock()
        parsed_url.netloc = "test.com"
        mock_urlparse.return_value = parsed_url

        with patch("apps.owasp.scraper.logger") as mock_logger:
            result = scraper.verify_url("https://test.com")
            mock_logger.exception.assert_called_once()
            assert result is None

    def test_verify_url_invalid_status(self, mock_urlparse, mock_session):
        scraper = OwaspScraper.__new__(OwaspScraper)
        scraper.session = mock_session

        parsed_url = MagicMock()
        parsed_url.netloc = "test.com"
        mock_urlparse.return_value = parsed_url

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_session.get.return_value = mock_response

        with patch("apps.owasp.scraper.logger") as mock_logger:
            result = scraper.verify_url("https://test.com")
            mock_logger.warning.assert_called_once()
            assert result is None
