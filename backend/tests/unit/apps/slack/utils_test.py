from unittest.mock import Mock
from urllib.parse import urljoin

import pytest
import requests as req
import yaml
from django.core.cache import cache
from lxml.etree import ParserError
from requests.exceptions import RequestException

from apps.common.constants import OWASP_NEWS_URL
from apps.owasp.models.project import Project
from apps.owasp.utils.gsoc import get_gsoc_projects
from apps.owasp.utils.news import get_news_data
from apps.owasp.utils.staff import STAFF_YAML_URL, get_staff_data
from apps.slack.utils import (
    download_file,
    escape,
    format_ai_response_for_slack,
    format_links_for_slack,
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


class TestFormatAiResponseForSlack:
    @pytest.mark.parametrize(
        ("input_text", "expected_output"),
        [
            ("", ""),
            (None, None),
            (
                "**OWASP ZAP** is a flagship project.",
                "*OWASP ZAP* is a flagship project.",
            ),
            (
                "This is __bold text__ in markdown.",
                "This is *bold text* in markdown.",
            ),
            (
                "### OWASP Top 10",
                "*OWASP Top 10*",
            ),
            (
                "## Chapter Meetings\nJoin our **local** chapters.",
                "*Chapter Meetings*\nJoin our *local* chapters.",
            ),
            (
                "### \nordinary text",
                "### \nordinary text",
            ),
            (
                "Check out [OWASP](https://owasp.org) for details.",
                "Check out <https://owasp.org|OWASP> for details.",
            ),
            (
                "```\nEntire block wrapped\n```",
                "Entire block wrapped",
            ),
            (
                "```python\n    print('hello')\n```",
                "    print('hello')",
            ),
            (
                "\r\n```python\r\n\r\n    print('hello')\r\n\r\n```\r\n",
                "    print('hello')",
            ),
            (
                "Here is code:\n```python\nprint('hello')\n```\nDone.",
                "Here is code:\nprint('hello')\nDone.",
            ),
            (
                "# **Bold heading**",
                "*Bold heading*",
            ),
            (
                "### Explore **OWASP** and __chapters__ with *contributors*",
                "*Explore OWASP and chapters with contributors*",
            ),
            ("# C* pointers", "*C* pointers*"),
            (
                "Here is code:\n```python\n# This is a comment\nx = 1\n```\nDone.",
                "Here is code:\n# This is a comment\nx = 1\nDone.",
            ),
            (
                "Run `poetry run pytest` now.",
                "Run poetry run pytest now.",
            ),
            (
                "Run ```curl --version``` now.",
                "Run curl --version now.",
            ),
            (
                "Before\n```sh\ncurl --version\n```\nRun ```curl --help``` now.",
                "Before\ncurl --version\nRun curl --help now.",
            ),
            (
                '```json {"a": 1}```',
                'json {"a": 1}',
            ),
            (
                "Before\n````python\n# Code\n**unchanged**\n````\nAfter",
                "Before\n# Code\n**unchanged**\nAfter",
            ),
            (
                "````markdown\n```python\n# Code\n```\n````",
                "```python\n# Code\n```",
            ),
            (
                "Contact <#C123|community> or <@U456>.",
                "Contact <#C123|community> or <@U456>.",
            ),
            (
                "```python\n# This is a comment\n**not bold**\nx = [1](https://example.com)\n```",
                "# This is a comment\n**not bold**\nx = [1](https://example.com)",
            ),
            (
                "Visit [OWASP](https://owasp.org):\n```markdown\n[example](https://example.com)\n```\nDone.",
                "Visit <https://owasp.org|OWASP>:\n[example](https://example.com)\nDone.",
            ),
        ],
    )
    def test_format_ai_response_for_slack(self, input_text, expected_output):
        """Test format_ai_response_for_slack with various markdown inputs."""
        assert format_ai_response_for_slack(input_text) == expected_output


class TestGetText:
    @pytest.mark.parametrize(
        ("input_blocks", "expected_output"),
        [
            (
                [{"type": "section", "text": {"type": "mrkdwn", "text": "Hello world"}}],
                "Hello world",
            ),
            (
                [{"type": "section", "text": {"type": "plain_text", "text": "Plain section"}}],
                "Plain section",
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

        monkeypatch.setattr(
            "apps.slack.utils.format.requests.get", Mock(return_value=mock_response)
        )

        result = download_file("https://files.slack.com/image.png", "xoxb-token")

        assert result == b"image-bytes"

    def test_download_file_http_error(self, monkeypatch):
        """Test download returns None on HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = req.HTTPError("404")

        monkeypatch.setattr(
            "apps.slack.utils.format.requests.get", Mock(return_value=mock_response)
        )

        result = download_file("https://files.slack.com/image.png", "xoxb-token")

        assert result is None

    def test_download_file_request_exception(self, monkeypatch):
        """Test download returns None on request exception."""
        monkeypatch.setattr(
            "apps.slack.utils.format.requests.get",
            Mock(side_effect=req.ConnectionError("timeout")),
        )

        result = download_file("https://files.slack.com/image.png", "xoxb-token")

        assert result is None

    def test_download_file_sends_auth_header(self, monkeypatch):
        """Test that download_file sends the correct authorization header."""
        mock_response = Mock()
        mock_response.content = b"image-bytes"
        mock_response.raise_for_status = Mock()
        mock_get = Mock(return_value=mock_response)

        monkeypatch.setattr("apps.slack.utils.format.requests.get", mock_get)

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

        def mock_filter(**_kwargs):
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
    def setup_method(self):
        """Clear Django cache before each news test."""
        cache.clear()

    def test_get_news_data(self, monkeypatch):
        """Test getting news data with mocked response."""
        mock_response = Mock()
        mock_response.content = MOCK_HTML_CONTENT.encode()
        mock_response.raise_for_status = Mock()

        mock_get = Mock(return_value=mock_response)

        monkeypatch.setattr("requests.get", mock_get)

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
        mock_response.raise_for_status = Mock()
        mock_get = Mock(return_value=mock_response)

        monkeypatch.setattr("requests.get", mock_get)

        result = get_news_data()

        assert len(result) == 1
        assert result[0]["title"] == "Title with anchor"

    @pytest.mark.parametrize("limit", [0, -1])
    def test_get_news_data_rejects_non_positive_limit(self, limit, monkeypatch):
        """Test get_news_data returns [] for non-positive limits without fetching."""
        mock_get = Mock()
        monkeypatch.setattr("requests.get", mock_get)

        assert get_news_data(limit=limit) == []
        mock_get.assert_not_called()

    def test_get_news_data_request_exception(self, monkeypatch):
        """Test get_news_data returns [] on request failures and does not cache them."""
        mock_get = Mock(side_effect=RequestException("Network error"))
        monkeypatch.setattr("requests.get", mock_get)

        assert get_news_data() == []
        assert get_news_data() == []
        assert mock_get.call_count == 2

    def test_get_news_data_empty_response_body(self, monkeypatch):
        """Test get_news_data returns [] for HTTP 200 with an empty body."""
        mock_response = Mock()
        mock_response.content = b""
        mock_response.raise_for_status = Mock()
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)

        assert get_news_data() == []
        mock_get.assert_called_once_with(OWASP_NEWS_URL, timeout=30)

    def test_get_news_data_parser_error(self, monkeypatch):
        """Test get_news_data returns [] when HTML parsing fails."""
        mock_response = Mock()
        mock_response.content = b"<html>"
        mock_response.raise_for_status = Mock()
        monkeypatch.setattr("requests.get", Mock(return_value=mock_response))
        monkeypatch.setattr(
            "apps.owasp.utils.news.html.fromstring",
            Mock(side_effect=ParserError("bad html")),
        )

        assert get_news_data() == []


class TestGetStaffData:
    def setup_method(self):
        """Clear Django cache before each staff test."""
        cache.clear()

    def test_get_staff_data(self, monkeypatch):
        """Test getting staff data with mocked response."""
        mock_response = Mock()
        mock_response.text = MOCK_STAFF_YAML
        mock_response.raise_for_status = Mock()
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)

        length = 3
        result = get_staff_data()
        assert len(result) == length
        assert result[0]["name"] == "Alice Smith"
        assert result[1]["name"] == "Bob Wilson"
        assert result[2]["name"] == "John Doe"

        mock_get.assert_called_once_with(STAFF_YAML_URL, timeout=30)

        result2 = get_staff_data()
        assert mock_get.call_count == 1
        assert result == result2

    def test_get_staff_data_request_exception(self, monkeypatch):
        """Test get_staff_data handles RequestException gracefully without caching None."""
        mock_get = Mock(side_effect=RequestException("Network error"))
        monkeypatch.setattr("requests.get", mock_get)

        assert get_staff_data() is None
        assert get_staff_data() is None
        assert mock_get.call_count == 2

    def test_get_staff_data_yaml_error(self, monkeypatch):
        """Test get_staff_data handles YAML parse errors."""
        mock_response = Mock()
        mock_response.text = "invalid: [\n  - broken"
        mock_response.raise_for_status = Mock()
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)

        assert get_staff_data() is None

    def test_get_staff_data_invalid_shape(self, monkeypatch):
        """Test get_staff_data rejects YAML that is not a list of named dicts."""
        mock_response = Mock()
        mock_response.text = yaml.dump({"name": "not a list"})
        mock_response.raise_for_status = Mock()
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)

        assert get_staff_data() is None

    def test_get_staff_data_missing_name(self, monkeypatch):
        """Test get_staff_data rejects staff entries without a name."""
        mock_response = Mock()
        mock_response.text = yaml.dump([{"title": "Developer"}])
        mock_response.raise_for_status = Mock()
        mock_get = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.get", mock_get)

        assert get_staff_data() is None
