from unittest.mock import Mock, patch
from urllib.parse import urljoin

import pytest
import requests as req
from requests.exceptions import RequestException

from apps.common.constants import OWASP_NEWS_URL
from apps.owasp.models.project import Project
from apps.owasp.utils.gsoc import get_gsoc_projects
from apps.owasp.utils.news import get_news_data
from apps.owasp.utils.staff import get_staff_data
from apps.slack.utils import (
    download_file,
    escape,
    format_links_for_slack,
    get_posts_data,
    get_sponsors_data,
    get_text,
    strip_markdown,
)

MOCK_GSOC_PROJECTS = {
    "2023": [
        {"idx_name": "Project1_2023", "idx_url": "https://example.com/proj1"},
        {"idx_name": "Project2_2023", "idx_url": "https://example.com/proj2"},
    ],
    "2024": [
        {"idx_name": "Project1_2024", "idx_url": "https://example.com/proj3"},
        {"idx_name": "Project2_2024", "idx_url": "https://example.com/proj4"},
    ],
}

MOCK_HTML_CONTENT = """
<html>
    <body>
        <h2><a href="/news1">News Title 1</a></h2>
        <p class="author">Author 1</p>
        <h2><a href="/news2">News Title 2</a></h2>
        <p class="author">Author 2</p>
        <h2><a href="/news3">News Title 3</a></h2>
        <p class="author">Author 3</p>
    </body>
</html>
"""

MOCK_STAFF_YAML = """
- name: John Doe
  title: Developer
  email: john@example.com
- name: Alice Smith
  title: Manager
  email: alice@example.com
- name: Bob Wilson
  title: Director
  email: bob@example.com
"""


class TestStripMarkdown:
    @pytest.mark.parametrize(
        ("input_text", "expected_output"),
        [
            (
                "Check out <https://owasp.org/supporters/list|current sponsors list>.",
                "Check out current sponsors list (https://owasp.org/supporters/list).",
            ),
            (
                "Visit <https://example.com|Example> for more details.",
                "Visit Example (https://example.com) for more details.",
            ),
            (
                "This is a *bold* text with a <https://example.com|link>.",
                "This is a bold text with a link (https://example.com).",
            ),
            (
                "No links here, just plain text.",
                "No links here, just plain text.",
            ),
            (
                "Multiple links: <https://example.com|First> and <https://example.org|Second>.",
                "Multiple links: First (https://example.com) and Second (https://example.org).",
            ),
        ],
    )
    def test_process_mrkdwn(self, input_text, expected_output):
        """Test the _process_mrkdwn function."""
        assert strip_markdown(input_text) == expected_output


class TestFormatLinksForSlack:
    @pytest.mark.parametrize(
        ("input_text", "expected_output"),
        [
            ("Check [link](https://example.com)", "Check <https://example.com|link>"),
            ("", ""),
            (None, None),
        ],
    )
    def test_format_links_for_slack(self, input_text, expected_output):
        """Test format_links_for_slack with various inputs including empty text."""
        assert format_links_for_slack(input_text) == expected_output


class TestGetText:
    @pytest.mark.parametrize(
        ("input_blocks", "expected_output"),
        [
            (
                [{"type": "section", "text": {"type": "mrkdwn", "text": "Hello world"}}],
                "Hello world",
            ),
            (
                [
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "This is a context block :smile: with a link here <https://example.com|link>",
                            }
                        ],
                    }
                ],
                "This is a context block :smile: with a link here link (https://example.com)",
            ),
            ([{"type": "divider"}], "---"),
            (
                [
                    {"type": "section", "text": {"type": "mrkdwn", "text": "*Bold* text"}},
                    {"type": "divider"},
                    {"type": "context", "elements": [{"type": "mrkdwn", "text": "Context text"}]},
                ],
                "Bold text\n---\nContext text",
            ),
            (
                [
                    {
                        "type": "actions",
                        "elements": [
                            {"type": "button", "text": {"text": "Click me", "type": "plain_text"}}
                        ],
                    }
                ],
                "Click me",
            ),
            (
                [
                    {
                        "type": "actions",
                        "elements": [
                            {"type": "button", "text": {"text": "Button 1", "type": "plain_text"}},
                            {"type": "button", "text": {"text": "Button 2", "type": "plain_text"}},
                            {"type": "overflow", "options": []},
                        ],
                    }
                ],
                "Button 1\nButton 2",
            ),
            (
                [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "Header text"},
                    }
                ],
                "Header text",
            ),
            (
                [
                    {
                        "type": "header",
                        "text": {"type": "mrkdwn", "text": "Markdown header"},
                    }
                ],
                "",
            ),
            (
                [
                    {
                        "type": "header",
                    }
                ],
                "",
            ),
            (
                [
                    {
                        "type": "image",
                        "image_url": "https://example.com/image.jpg",
                        "alt_text": "Example",
                    }
                ],
                "Image: https://example.com/image.jpg",
            ),
            (
                [
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": "Field 1"},
                            {"type": "mrkdwn", "text": "Field 2"},
                        ],
                    }
                ],
                "Field 1\nField 2",
            ),
            (
                [{"type": "unknown_block_type", "data": "something"}],
                "",
            ),
        ],
    )
    def test_blocks_to_text(self, input_blocks, expected_output):
        """Test the blocks_to_text function."""
        assert get_text(input_blocks) == expected_output


class TestDownloadFile:
    def test_download_file_success(self, monkeypatch):
        """Test successful file download."""
        mock_response = Mock()
        mock_response.content = b"image-bytes"
        mock_response.raise_for_status = Mock()

        monkeypatch.setattr("apps.slack.utils.requests.get", Mock(return_value=mock_response))

        result = download_file("https://files.slack.com/image.png", "xoxb-token")

        assert result == b"image-bytes"

    def test_download_file_http_error(self, monkeypatch):
        """Test download returns None on HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = req.HTTPError("404")

        monkeypatch.setattr("apps.slack.utils.requests.get", Mock(return_value=mock_response))

        result = download_file("https://files.slack.com/image.png", "xoxb-token")

        assert result is None

    def test_download_file_request_exception(self, monkeypatch):
        """Test download returns None on request exception."""
        monkeypatch.setattr(
            "apps.slack.utils.requests.get", Mock(side_effect=req.ConnectionError("timeout"))
        )

        result = download_file("https://files.slack.com/image.png", "xoxb-token")

        assert result is None

    def test_download_file_sends_auth_header(self, monkeypatch):
        """Test that download_file sends the correct authorization header."""
        mock_response = Mock()
        mock_response.content = b"image-bytes"
        mock_response.raise_for_status = Mock()
        mock_get = Mock(return_value=mock_response)

        monkeypatch.setattr("apps.slack.utils.requests.get", mock_get)

        download_file("https://files.slack.com/image.png", "xoxb-test-token")

        mock_get.assert_called_once_with(
            "https://files.slack.com/image.png",
            headers={"Authorization": "Bearer xoxb-test-token"},
            timeout=30,
        )


class TestEscape:
    @pytest.mark.parametrize(
        ("input_content", "expected_output"),
        [
            ("<script>alert('XSS')</script>", "&lt;script&gt;alert('XSS')&lt;/script&gt;"),
            ("Hello, World!", "Hello, World!"),
            (
                "<b>Bold</b> & <i>Italic</i>",
                "&lt;b&gt;Bold&lt;/b&gt; &amp; &lt;i&gt;Italic&lt;/i&gt;",
            ),
        ],
    )
    def test_escape(self, input_content, expected_output):
        """Test the escape function."""
        assert escape(input_content) == expected_output


class TestGetGsocProjects:
    def test_get_gsoc_projects(self, monkeypatch):
        """Test getting GSoC projects with mocked database data."""
        # Create mock project objects
        mock_project1 = Mock(spec=Project)
        mock_project1.name = "Project1_2023"
        mock_project1.key = "www-project-project1"
        mock_project1.owasp_url = "https://example.com/proj1"
        mock_project1.custom_tags = ["gsoc2023", "security"]

        mock_project2 = Mock(spec=Project)
        mock_project2.name = "Project2_2023"
        mock_project2.key = "www-project-project2"
        mock_project2.owasp_url = "https://example.com/proj2"
        mock_project2.custom_tags = ["gsoc2023", "testing"]

        # Mock the QuerySet chain: filter().only().order_by()
        projects_list = [mock_project1, mock_project2]

        mock_order_by_result = projects_list
        mock_order_by = Mock(return_value=mock_order_by_result)

        mock_only_result = Mock()
        mock_only_result.order_by = mock_order_by

        mock_only = Mock(return_value=mock_only_result)

        mock_queryset = Mock()
        mock_queryset.only = mock_only

        def mock_filter(**kwargs):
            return mock_queryset

        monkeypatch.setattr(Project.objects, "filter", mock_filter)
        get_gsoc_projects.cache_clear()

        result = get_gsoc_projects(2023)
        length = 2
        assert len(result) == length
        assert result[0]["name"] == "Project1_2023"
        assert result[0]["url"] == "https://example.com/proj1"
        assert result[1]["name"] == "Project2_2023"
        assert result[1]["url"] == "https://example.com/proj2"

        # Test caching - should return same result without another query
        result2 = get_gsoc_projects(2023)
        assert result == result2


class TestGetNewsData:
    def test_get_news_data(self, monkeypatch):
        """Test getting news data with mocked response."""
        mock_response = Mock()
        mock_response.content = MOCK_HTML_CONTENT.encode()

        mock_get = Mock(return_value=mock_response)

        monkeypatch.setattr("requests.get", mock_get)
        get_news_data.cache_clear()

        result = get_news_data()
        length = 3
        assert len(result) == length
        assert result[0]["title"] == "News Title 1"
        assert result[0]["author"] == "Author 1"
        assert result[0]["url"] == urljoin(OWASP_NEWS_URL, "/news1")

        length = 2
        result_limited = get_news_data(limit=2)
        assert len(result_limited) == length

        mock_get.assert_called_with(OWASP_NEWS_URL, timeout=30)
        result2 = get_news_data()
        assert mock_get.call_count == length
        assert result == result2

    def test_get_news_data_with_missing_anchor(self, monkeypatch):
        """Test getting news data when h2 tags don't have anchors."""
        mock_html = """
        <html>
            <body>
                <h2>Title without anchor</h2>
                <p class="author">Author 1</p>
                <h2><a href="/news2">Title with anchor</a></h2>
                <p class="author">Author 2</p>
            </body>
        </html>
        """
        mock_response = Mock()
        mock_response.content = mock_html.encode()
        mock_get = Mock(return_value=mock_response)

        monkeypatch.setattr("requests.get", mock_get)
        get_news_data.cache_clear()

        result = get_news_data()

        assert len(result) == 1
        assert result[0]["title"] == "Title with anchor"


class TestGetStaffData:
    def test_get_staff_data(self, monkeypatch):
        """Test getting staff data with mocked response."""
        mock_response = Mock()
        mock_response.text = MOCK_STAFF_YAML
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)
        get_staff_data.cache_clear()

        length = 3
        result = get_staff_data()
        assert len(result) == length
        assert result[0]["name"] == "Alice Smith"
        assert result[1]["name"] == "Bob Wilson"
        assert result[2]["name"] == "John Doe"

        mock_get.assert_called_once_with(
            "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/staff.yml",
            timeout=30,
        )

    def test_get_staff_data_request_exception(self, monkeypatch):
        """Test get_staff_data handles RequestException gracefully."""
        mock_get = Mock(side_effect=RequestException("Network error"))
        monkeypatch.setattr("requests.get", mock_get)
        get_staff_data.cache_clear()

        result = get_staff_data()
        assert result is None


class TestGetSponsorsData:
    def test_get_sponsors_data(self):
        """Test get_sponsors_data returns sponsors queryset."""
        mock_sponsor = Mock()
        mock_queryset = Mock()
        mock_queryset.__getitem__ = Mock(return_value=[mock_sponsor])

        with patch("apps.owasp.models.sponsor.Sponsor.objects") as mock_objects:
            mock_objects.all.return_value = mock_queryset

            result = get_sponsors_data(limit=5)
            mock_objects.all.assert_called_once()
            assert result is not None

    def test_get_sponsors_data_exception(self):
        """Test get_sponsors_data handles exceptions gracefully."""
        with patch("apps.owasp.models.sponsor.Sponsor.objects") as mock_objects:
            mock_objects.all.side_effect = Exception("Database error")

            result = get_sponsors_data()
            assert result is None


class TestGetPostsData:
    def test_get_posts_data(self):
        """Test get_posts_data returns posts queryset."""
        mock_post = Mock()
        mock_queryset = Mock()
        mock_queryset.__getitem__ = Mock(return_value=[mock_post])

        with patch("apps.owasp.models.post.Post.recent_posts") as mock_recent:
            mock_recent.return_value = mock_queryset
            get_posts_data.cache_clear()

            result = get_posts_data(limit=3)
            mock_recent.assert_called_once()
            assert result is not None

    def test_get_posts_data_exception(self):
        """Test get_posts_data handles exceptions gracefully."""
        with patch("apps.owasp.models.post.Post.recent_posts") as mock_recent:
            mock_recent.side_effect = Exception("Database error")
            get_posts_data.cache_clear()

            result = get_posts_data()
            assert result is None
