import logging
from http import HTTPStatus
from unittest import mock
from unittest.mock import Mock, patch

import pytest
import requests
from lxml import etree

from apps.owasp.sync import OwaspSync


class TestOwaspSync:
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
            <html>
                <header><a href="https://owasp.org/header">Home</a></header>
                <div>
                    <h3>Project Leaders</h3>
                    <div>
                        <h4>Leader One</h4>
                        <a href="mailto:leader.one@owasp.org">Email</a>
                        <a href="https://github.com/leader-one">GitHub</a>
                    </div>
                    <div>
                        <h4>Leader Two</h4>
                        <a href="https://owasp.org/link1">Docs</a>
                    </div>
                </div>
                <a href="https://example.com/url2">URL 2</a>
                <a href="https://owasp.org/url1">URL 1</a>
                <footer><a href="https://owasp.org/footer">Footer</a></footer>
            </html>
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
            sync = OwaspSync("https://test.org")

        assert sync.page_tree is None

    def test_verify_url_redirect_chain(self, mock_session, mock_response):
        """Test URL verification with redirect chain."""
        mock_session.get.return_value = mock_response
        sync = OwaspSync("https://test.org")
        mock_session.get.reset_mock()

        redirect_response = Mock()
        redirect_response.status_code = HTTPStatus.MOVED_PERMANENTLY
        redirect_response.headers = {"Location": "https://new-url.org"}

        final_response = Mock()
        final_response.status_code = HTTPStatus.OK
        mock_session.get.side_effect = [redirect_response, final_response]

        assert sync.verify_url("https://old-url.org") == "https://new-url.org"

    def test_verify_url_resolves_a_relative_redirect(self, mock_session, mock_response):
        """Test a relative Location is resolved against the current URL."""
        mock_session.get.return_value = mock_response
        sync = OwaspSync("https://test.org")
        mock_session.get.reset_mock()

        redirect_response = Mock()
        redirect_response.status_code = HTTPStatus.FOUND
        redirect_response.headers = {"Location": "/groups/events-committee"}
        final_response = Mock()
        final_response.status_code = HTTPStatus.OK
        mock_session.get.side_effect = [redirect_response, final_response]

        assert (
            sync.verify_url("https://owasp.org/old") == "https://owasp.org/groups/events-committee"
        )

    def test_verify_url_stops_following_a_redirect_loop(self, mock_session, mock_response):
        """Test a redirect loop is left unverified instead of recursing forever."""
        mock_session.get.return_value = mock_response
        sync = OwaspSync("https://test.org")
        mock_session.get.reset_mock()

        redirect_response = Mock()
        redirect_response.status_code = HTTPStatus.FOUND
        redirect_response.headers = {"Location": "https://loop.example/a"}
        mock_session.get.return_value = redirect_response

        assert sync.verify_url("https://loop.example/a") == "https://loop.example/a"
        assert mock_session.get.call_count == 6

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
        sync = OwaspSync("https://test.org")
        mock_session.get.reset_mock()

        redirect_response = Mock()
        redirect_response.status_code = status_code
        redirect_response.headers = {"Location": "https://new-url.org"}

        final_response = Mock()
        final_response.status_code = HTTPStatus.OK
        mock_session.get.side_effect = [redirect_response, final_response]

        assert sync.verify_url("https://old-url.org") == "https://new-url.org"
        assert mock_session.get.call_count >= 1

    def test_initialization_not_found(self, mock_session):
        response = Mock()
        response.status_code = HTTPStatus.NOT_FOUND
        mock_session.get.return_value = response

        sync = OwaspSync("https://test.org")

        assert sync.page_tree is None

    def test_verify_url_invalid_url(self, mock_session):
        response = Mock()
        response.status_code = HTTPStatus.OK
        response.content = b"<html></html>"
        mock_session.get.return_value = response

        sync = OwaspSync("https://test.org")

        assert sync.verify_url("invalid-url") is None

    def test_verify_url_unsupported_status_code(self, mock_session):
        response = Mock()
        response.status_code = HTTPStatus.IM_A_TEAPOT
        response.content = b"<html></html>"
        mock_session.get.return_value = response

        sync = OwaspSync("https://test.org")

        assert sync.verify_url("https://test.org") is None

    def test_verify_url_logs_warning(self, mock_session, caplog):
        response = Mock()
        response.status_code = HTTPStatus.FORBIDDEN
        response.content = b"<html></html>"
        mock_session.get.return_value = response

        sync = OwaspSync("https://test.org")
        with caplog.at_level(logging.WARNING):
            result = sync.verify_url("https://test.org")

        assert result is None
        assert "Couldn't verify URL" in caplog.text

    def test_get_urls_with_domain(self, mock_session, sample_html):
        mock_response = Mock()
        mock_response.content = sample_html
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response

        sync = OwaspSync("https://test.org")

        assert sync.get_urls(domain="owasp.org") == {
            "https://owasp.org/link1",
            "https://owasp.org/url1",
        }

    def test_initialization_request_exception(self, mock_session):
        """Test initialization with a RequestException."""
        mock_session.get.side_effect = requests.exceptions.RequestException

        sync = OwaspSync("https://test.org")

        assert sync.page_tree is None

    def test_get_urls_no_domain(self, mock_session, sample_html):
        """Test get_urls without providing a domain."""
        mock_response = Mock()
        mock_response.content = sample_html
        mock_response.status_code = 200  # Added status code
        mock_session.get.return_value = mock_response

        sync = OwaspSync("https://test.org")

        assert sync.get_urls() == {
            "https://github.com/leader-one",
            "https://owasp.org/link1",
            "https://example.com/url2",
            "https://owasp.org/url1",
        }

    def test_verify_url_supported_domain(self, mock_session):
        """Test verify_url with a supported domain."""
        response = Mock()
        response.status_code = HTTPStatus.OK
        response.content = b"<html></html>"
        mock_session.get.return_value = response

        sync = OwaspSync("https://test.org")

        assert (
            sync.verify_url("https://www.linkedin.com/in/test")
            == "https://www.linkedin.com/in/test"
        )

    def test_get_urls_empty_page(self, mock_session):
        """Test get_urls when the page body has no links."""
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = b"<html><body><p>No links</p></body></html>"
        mock_session.get.return_value = mock_response

        sync = OwaspSync("https://test.org")

        assert sync.get_urls() == set()

    def test_initialization_timeout(self, mock_session):
        """Test initialization with a timeout exception."""
        mock_session.get.side_effect = requests.exceptions.Timeout
        sync = OwaspSync("https://test.org")

        assert sync.page_tree is None

    def test_get_leaders_with_none_page_tree(self, mock_session):
        """Test get_leaders returns an empty dict when the request fails."""
        mock_session.get.side_effect = requests.exceptions.RequestException
        sync = OwaspSync("https://test.org")

        assert sync.page_tree is None
        assert sync.get_leaders() == {}

    def test_get_leaders_from_project_cards(self, mock_session, sample_html):
        """Test get_leaders reads names and emails from project leader cards."""
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = sample_html
        mock_session.get.return_value = mock_response

        sync = OwaspSync("https://test.org")

        assert sync.get_leaders() == {
            "Leader One": "leader.one@owasp.org",
            "Leader Two": None,
        }

    def test_get_leaders_from_chapter_cards(self, mock_session):
        """Test get_leaders reads names and emails from chapter leader cards."""
        chapter_html = b"""
            <section>
                <h2>Chapter Leaders</h2>
                <div>
                    <h3>Sam Stepanyan</h3>
                    <a href="mailto:sam.stepanyan@owasp.org?subject=Hi">Email</a>
                </div>
            </section>
        """
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = chapter_html
        mock_session.get.return_value = mock_response

        sync = OwaspSync("https://test.org")

        assert sync.get_leaders() == {"Sam Stepanyan": "sam.stepanyan@owasp.org"}

    def test_get_leaders_without_section(self, mock_session):
        """Test get_leaders returns an empty dict when the page has no leader section."""
        mock_response = Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = b"<html><body><h2>About</h2><p>No leaders here</p></body></html>"
        mock_session.get.return_value = mock_response

        sync = OwaspSync("https://test.org")

        assert sync.get_leaders() == {}

    def test_page_url(self):
        """Test public page URLs for projects, chapters, and committees."""
        assert OwaspSync.page_url("project", "nest") == "https://owasp.org/projects/nest"
        assert OwaspSync.page_url("chapter", "london") == "https://owasp.org/chapters/london"
        assert (
            OwaspSync.page_url("committee", "board") == "https://owasp.org/groups/board-committee"
        )

    def test_apply_leaders_leaves_entity_unchanged(self):
        """Test stored leaders stay in place when the page has no leader information."""
        entity = Mock()
        entity.leaders_raw = ["Existing Leader"]

        OwaspSync.apply_leaders(entity, {})

        assert entity.leaders_raw == ["Existing Leader"]
        entity.sync_leaders.assert_not_called()

    def test_apply_leaders_stores_found_leaders(self):
        """Test found leader cards replace stored leaders."""
        entity = Mock()
        leaders = {"Leader One": "leader.one@owasp.org"}

        OwaspSync.apply_leaders(entity, leaders)

        assert entity.leaders_raw == ["Leader One"]
        entity.sync_leaders.assert_called_once_with(leaders)

    def test_verify_url_request_exception(self, mock_session, mock_response, caplog):
        """Test verify_url handles request exceptions during verification."""
        mock_session.get.return_value = mock_response
        sync = OwaspSync("https://test.org")
        mock_session.get.reset_mock()

        mock_session.get.side_effect = requests.exceptions.RequestException("Connection error")

        with caplog.at_level(logging.ERROR):
            result = sync.verify_url("https://example.org")

        assert result == "https://example.org"
        assert "Request failed" in caplog.text

    def test_urls_with_none_page_tree(self, mock_session):
        """Test get_urls returns empty set when request fails (page_tree is None)."""
        mock_session.get.side_effect = requests.exceptions.RequestException

        sync = OwaspSync("https://test.org")

        assert sync.page_tree is None
        assert sync.get_urls() == set()
        mock_session.get.assert_called_once()

    @mock.patch("requests.Session.get")
    def test_request_exception_sets_failure_flag(self, mock_get):
        """Test that a network exception sets is_request_failed to True."""
        mock_get.side_effect = requests.exceptions.RequestException()
        sync = OwaspSync("https://example.com")

        assert sync.is_request_failed is True

    @mock.patch("requests.Session.get")
    def test_5xx_server_error_sets_failure_flag(self, mock_get):
        """Test that a 500 server error sets is_request_failed to True."""
        mock_response = mock.Mock()
        mock_response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        mock_get.return_value = mock_response
        sync = OwaspSync("https://example.com")

        assert sync.is_request_failed is True

    @mock.patch("requests.Session.get")
    def test_404_not_found_leaves_failure_flag_false(self, mock_get):
        """Test that a 404 Not Found leaves is_request_failed as False."""
        mock_response = mock.Mock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_get.return_value = mock_response
        sync = OwaspSync("https://example.com")

        assert sync.is_request_failed is False
