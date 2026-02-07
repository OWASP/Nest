import logging
from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest
import requests
from lxml import etree

from apps.owasp.scraper import OwaspScraper


class TestOwaspScraper:
    @pytest.fixture
    def mock_session(self):
        """Fixture to provide a mock session."""
        with patch("requests.Session") as mock:
            session = Mock()
            mock.return_value = session
            yield session

    @pytest.fixture
    def sample_html(self):
        """Fixture to provide sample HTML content."""
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

    @pytest.fixture
    def mock_response(self, sample_html):
        """Fixture to provide a mock response."""
        response = Mock()
        response.status_code = HTTPStatus.OK
        response.content = sample_html
        return response

    def test_initialization_parser_error(self, mock_session):
        """Test initialization with parser error."""
        response = Mock()
        response.status_code = HTTPStatus.OK
        response.content = b"<completely invalid>> html"
        mock_session.get.return_value = response
        mock_parser = Mock(side_effect=etree.ParserError("Parser error"))

        with patch("lxml.html.fromstring", mock_parser):
            scraper = OwaspScraper("https://test.org")

        assert scraper.page_tree is None

    def test_verify_url_redirect_chain(self, mock_session, mock_response):
        """Test URL verification with redirect chain."""
        mock_session.get.return_value = mock_response
        scraper = OwaspScraper("https://test.org")
        mock_session.get.reset_mock()

        redirect_response = Mock()
        redirect_response.status_code = HTTPStatus.MOVED_PERMANENTLY
        redirect_response.headers = {"Location": "https://new-url.org"}

        final_response = Mock()
        final_response.status_code = HTTPStatus.OK
        mock_session.get.side_effect = [redirect_response, final_response]

        assert scraper.verify_url("https://old-url.org") == "https://new-url.org"

    @pytest.mark.parametrize(
        "status_code",
        [
            HTTPStatus.MOVED_PERMANENTLY,  # 301
            HTTPStatus.FOUND,  # 302
            HTTPStatus.SEE_OTHER,  # 303
            HTTPStatus.TEMPORARY_REDIRECT,  # 307
            HTTPStatus.PERMANENT_REDIRECT,  # 308
        ],
    )
    def test_verify_url_redirect_status_codes(self, mock_session, mock_response, status_code):
        """Test URL verification with different redirect status codes."""
        mock_session.get.return_value = mock_response
        scraper = OwaspScraper("https://test.org")
        mock_session.get.reset_mock()

        redirect_response = Mock()
        redirect_response.status_code = status_code
        redirect_response.headers = {"Location": "https://new-url.org"}

        final_response = Mock()
        final_response.status_code = HTTPStatus.OK
        mock_session.get.side_effect = [redirect_response, final_response]

        assert scraper.verify_url("https://old-url.org") == "https://new-url.org"
        assert mock_session.get.call_count >= 1

    def test_initialization_not_found(self, mock_session):
        response = Mock()
        response.status_code = HTTPStatus.NOT_FOUND
        mock_session.get.return_value = response

        scraper = OwaspScraper("https://test.org")

        assert scraper.page_tree is None

    def test_verify_url_invalid_url(self, mock_session):
        response = Mock()
        response.status_code = HTTPStatus.OK
        response.content = b"<html></html>"
        mock_session.get.return_value = response

        scraper = OwaspScraper("https://test.org")

        assert scraper.verify_url("invalid-url") is None

    def test_verify_url_unsupported_status_code(self, mock_session):
        response = Mock()
        response.status_code = HTTPStatus.IM_A_TEAPOT
        response.content = b"<html></html>"
        mock_session.get.return_value = response

        scraper = OwaspScraper("https://test.org")

        assert scraper.verify_url("https://test.org") is None

    def test_verify_url_logs_warning(self, mock_session, caplog):
        response = Mock()
        response.status_code = HTTPStatus.FORBIDDEN
        response.content = b"<html></html>"
        mock_session.get.return_value = response

        scraper = OwaspScraper("https://test.org")
        with caplog.at_level(logging.WARNING):
            result = scraper.verify_url("https://test.org")

        assert result is None
        assert "Couldn't verify URL" in caplog.text

    def test_get_urls_with_domain(self, mock_session, sample_html):
        mock_response = Mock()
        mock_response.content = sample_html
        mock_session.get.return_value = mock_response

        scraper = OwaspScraper("https://test.org")

        assert scraper.get_urls(domain="owasp.org") == {
            "https://owasp.org/link1",
            "https://owasp.org/link2",
            "https://owasp.org/link3",
            "https://owasp.org/url1",
            "https://owasp.org/url3",
        }

    def test_initialization_request_exception(self, mock_session):
        """Test initialization with a RequestException."""
        mock_session.get.side_effect = requests.exceptions.RequestException

        scraper = OwaspScraper("https://test.org")

        assert scraper.page_tree is None

    def test_get_urls_no_domain(self, mock_session, sample_html):
        """Test get_urls without providing a domain."""
        mock_response = Mock()
        mock_response.content = sample_html
        mock_session.get.return_value = mock_response

        scraper = OwaspScraper("https://test.org")

        assert scraper.get_urls() == {
            "https://owasp.org/link1",
            "https://owasp.org/link2",
            "https://owasp.org/link3",
            "https://owasp.org/url1",
            "https://example.com/url2",
            "https://owasp.org/url3",
        }

    def test_verify_url_supported_domain(self, mock_session):
        """Test verify_url with a supported domain."""
        response = Mock()
        response.status_code = HTTPStatus.OK
        response.content = b"<html></html>"
        mock_session.get.return_value = response

        scraper = OwaspScraper("https://test.org")

        assert (
            scraper.verify_url("https://www.linkedin.com/in/test")
            == "https://www.linkedin.com/in/test"
        )

    def test_get_urls_empty_sidebar(self, mock_session):
        """Test get_urls when the sidebar is empty."""
        empty_html = b"<div class='sidebar'></div>"
        mock_response = Mock()
        mock_response.content = empty_html
        mock_session.get.return_value = mock_response

        scraper = OwaspScraper("https://test.org")

        assert scraper.get_urls() == set()

    def test_initialization_timeout(self, mock_session):
        """Test initialization with a timeout exception."""
        mock_session.get.side_effect = requests.exceptions.Timeout
        scraper = OwaspScraper("https://test.org")

        assert scraper.page_tree is None

    def test_get_audience_with_none_page_tree(self, mock_session):
        """Test get_audience returns empty list when page_tree is None."""
        mock_session.get.side_effect = requests.exceptions.RequestException
        scraper = OwaspScraper("https://test.org")

        assert scraper.page_tree is None
        assert scraper.get_audience() == []

    def test_get_audience_with_text_content(self, mock_session):
        """Test get_audience extracts audience from text content in sidebar."""
        html_with_audience = (
            b'<div class="sidebar"><ul><li>For Builders</li><li>For Defenders</li></ul></div>'
        )
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = html_with_audience
        mock_session.get.return_value = mock_response

        scraper = OwaspScraper("https://test.org")
        audience = scraper.get_audience()

        assert "builder" in audience
        assert "defender" in audience

    def test_get_audience_with_paragraph_content(self, mock_session):
        """Test get_audience extracts audience from paragraph text."""
        html_with_audience = b'<div class="sidebar"><p>For Breakers</p></div>'
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = html_with_audience
        mock_session.get.return_value = mock_response

        scraper = OwaspScraper("https://test.org")
        audience = scraper.get_audience()

        assert "breaker" in audience

    def test_get_audience_with_image_alt_text(self, mock_session):
        """Test get_audience extracts audience from image alt text."""
        html_with_audience = (
            b'<div class="sidebar"><img src="test.jpg" alt="For Builders" /></div>'
        )
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = html_with_audience
        mock_session.get.return_value = mock_response

        scraper = OwaspScraper("https://test.org")
        audience = scraper.get_audience()

        assert "builder" in audience

    def test_get_audience_with_complementary_role(self, mock_session):
        """Test get_audience works with complementary role containers."""
        html_with_audience = b'<div role="complementary"><p>For Defenders</p></div>'
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = html_with_audience
        mock_session.get.return_value = mock_response

        scraper = OwaspScraper("https://test.org")
        audience = scraper.get_audience()

        assert "defender" in audience

    def test_get_audience_with_empty_text_content(self, mock_session):
        """Test get_audience handles empty text content."""
        html_with_empty = b'<div class="sidebar"></div>'
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = html_with_empty
        mock_session.get.return_value = mock_response

        scraper = OwaspScraper("https://test.org")
        audience = scraper.get_audience()

        assert audience == []

    def test_get_audience_with_empty_alt_text(self, mock_session):
        """Test get_audience handles images with no alt text."""
        html_with_no_alt = b'<div class="sidebar"><img src="test.jpg" alt="" /></div>'
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = html_with_no_alt
        mock_session.get.return_value = mock_response

        scraper = OwaspScraper("https://test.org")
        audience = scraper.get_audience()

        assert audience == []

    def test_get_audience_returns_sorted_list(self, mock_session):
        """Test get_audience returns sorted unique audience list."""
        html_with_all = (
            b'<div class="sidebar"><ul><li>For Builders</li></ul>'
            b"<p>For Defenders</p><p>For Breakers</p></div>"
        )
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = html_with_all
        mock_session.get.return_value = mock_response

        scraper = OwaspScraper("https://test.org")
        audience = scraper.get_audience()

        assert audience == ["breaker", "builder", "defender"]

    def test_verify_url_request_exception(self, mock_session, mock_response, caplog):
        """Test verify_url handles request exceptions during verification."""
        mock_session.get.return_value = mock_response
        scraper = OwaspScraper("https://test.org")
        mock_session.get.reset_mock()

        mock_session.get.side_effect = requests.exceptions.RequestException("Connection error")

        with caplog.at_level(logging.WARNING):
            result = scraper.verify_url("https://example.org")

        assert result is None
        assert "Couldn't verify URL" in caplog.text or "Connection error" in caplog.text
