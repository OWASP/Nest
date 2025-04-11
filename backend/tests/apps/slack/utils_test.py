"""Tests for Slack utils."""

from unittest.mock import MagicMock, Mock, patch
from urllib.parse import urljoin

import pytest
import yaml
from requests.exceptions import RequestException

from apps.common.constants import OWASP_NEWS_URL
from apps.slack.utils import (
    escape,
    get_events_data,
    get_gsoc_projects,
    get_news_data,
    get_sponsors_data,
    get_staff_data,
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

news_title = "News Title"
news_url = "/news-url"
href_query = ".//a[@href]"
author_name = "Author Name"
database_error = "Database error"


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
        (
            "*Bold* _Italic_ ~Strike~ text with **double asterisks**.",
            "Bold _Italic_ ~Strike~ text with double asterisks.",
        ),
        (
            "<https://example.com|Link with *formatting* inside>",
            "Link with formatting inside (https://example.com)",
        ),
        (
            "Text with <https://example.com|incomplete link and *bold text*>.",
            "Text with incomplete link and bold text (https://example.com).",
        ),
        (
            "Multiple *asterisk* pairs *in* *one* string",
            "Multiple asterisk pairs in one string",
        ),
        (
            "Text with *asterisks* and <http://localhost:8000|local link>",
            "Text with asterisks and local link (http://localhost:8000)",
        ),
    ],
)
def test_process_mrkdwn(input_text, expected_output):
    """Test the strip_markdown function."""
    assert strip_markdown(input_text) == expected_output


@pytest.mark.parametrize(
    ("input_blocks", "expected_output"),
    [
        ([{"type": "section", "text": {"type": "mrkdwn", "text": "Hello world"}}], "Hello world"),
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
            [{"type": "header", "text": {"type": "plain_text", "text": "Header text"}}],
            "Header text",
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
    ],
)
def test_blocks_to_text(input_blocks, expected_output):
    """Test the blocks_to_text function."""
    assert get_text(input_blocks) == expected_output


@pytest.mark.parametrize(
    ("input_content", "expected_output"),
    [
        ("<script>alert('XSS')</script>", "&lt;script&gt;alert('XSS')&lt;/script&gt;"),
        ("Hello, World!", "Hello, World!"),
        ("<b>Bold</b> & <i>Italic</i>", "&lt;b&gt;Bold&lt;/b&gt; &amp; &lt;i&gt;Italic&lt;/i&gt;"),
    ],
)
def test_escape(input_content, expected_output):
    """Test the escape function."""
    assert escape(input_content) == expected_output


def test_get_gsoc_projects_(monkeypatch):
    """Test getting GSoC projects with mocked data."""
    mock_get_projects = Mock()
    mock_get_projects.return_value = {"hits": MOCK_GSOC_PROJECTS["2023"]}

    monkeypatch.setattr("apps.owasp.api.search.project.get_projects", mock_get_projects)

    result = get_gsoc_projects("2023")
    length = 2
    assert len(result) == length
    assert result[0]["idx_name"] == "Project1_2023"
    assert result[1]["idx_url"] == "https://example.com/proj2"

    mock_get_projects.assert_called_once_with(
        attributes=["idx_name", "idx_url"],
        query="gsoc2023",
        searchable_attributes=[
            "idx_custom_tags",
            "idx_languages",
            "idx_tags",
            "idx_topics",
        ],
    )

    result2 = get_gsoc_projects("2023")
    assert mock_get_projects.call_count == 1
    assert result == result2


def test_get_news_data(monkeypatch):
    """Test getting news data with mocked response."""
    mock_response = Mock()
    mock_response.content = MOCK_HTML_CONTENT.encode()

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


def test_get_staff_data(monkeypatch):
    """Test getting staff data with mocked response."""
    mock_response = Mock()
    mock_response.text = MOCK_STAFF_YAML
    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr("requests.get", mock_get)
    length = 3
    result = get_staff_data()
    assert len(result) == length
    assert result[0]["name"] == "Alice Smith"
    assert result[1]["name"] == "Bob Wilson"
    assert result[2]["name"] == "John Doe"

    mock_get.assert_called_once_with(
        "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/staff.yml", timeout=30
    )


@patch("apps.owasp.api.search.project.get_projects")
def test_get_gsoc_projects(mock_get_projects):
    """Test get_gsoc_projects function."""
    mock_get_projects.return_value = {"hits": ["project1", "project2"]}
    year = 2023

    result = get_gsoc_projects(year)

    mock_get_projects.assert_called_once_with(
        attributes=["idx_name", "idx_url"],
        query=f"gsoc{year}",
        searchable_attributes=[
            "idx_custom_tags",
            "idx_languages",
            "idx_tags",
            "idx_topics",
        ],
    )
    assert result == ["project1", "project2"]


@patch("requests.get")
@patch("lxml.html.fromstring")
def test_get_news_data_with_patches(mock_fromstring, mock_requests_get):
    """Test get_news_data function."""
    mock_response = MagicMock()
    mock_requests_get.return_value = mock_response

    mock_tree = MagicMock()
    mock_fromstring.return_value = mock_tree

    mock_h2 = MagicMock()
    mock_tree.xpath.return_value = [mock_h2]

    mock_anchor = MagicMock()
    mock_anchor.text_content = MagicMock(return_value=news_title)
    mock_anchor.get.return_value = news_url
    mock_h2.xpath.side_effect = lambda query: [mock_anchor] if query == href_query else []

    result = get_news_data(limit=1)

    assert result == [
        {
            "author": "",
            "title": news_title,
            "url": urljoin(OWASP_NEWS_URL, news_url),
        }
    ]

    get_news_data.cache_clear()

    mock_h2_with_author = MagicMock()
    mock_author_tag = MagicMock()
    mock_author_tag.text_content.return_value = author_name
    mock_h2_with_author.xpath.side_effect = lambda query: (
        [mock_anchor] if query == href_query else evaluate_author_query(query)
    )

    def evaluate_author_query(query):
        return [mock_author_tag] if query == "./following-sibling::p[@class='author']" else []

    mock_tree.xpath.return_value = [mock_h2_with_author]

    result = get_news_data(limit=1)

    assert result == [
        {
            "author": author_name,
            "title": news_title,
            "url": urljoin(OWASP_NEWS_URL, news_url),
        }
    ]

    get_news_data.cache_clear()
    mock_h2_without_anchor = MagicMock()
    mock_h2_without_anchor.xpath.side_effect = list

    mock_h2_with_author = MagicMock()
    mock_h2_with_author.xpath.side_effect = lambda query: (
        [mock_anchor] if query == href_query else evaluate_author_query(query)
    )

    mock_tree.xpath.return_value = [mock_h2_without_anchor, mock_h2_with_author]

    result = get_news_data(limit=1)

    assert result == [
        {
            "author": author_name,
            "title": news_title,
            "url": urljoin(OWASP_NEWS_URL, news_url),
        }
    ]


@patch("requests.get")
def test_get_staff_data_success(mock_requests_get):
    """Test get_staff_data function with successful response."""
    mock_response = MagicMock()
    mock_response.text = """
    - name: Person B
      title: Title B
    - name: Person A
      title: Title A
    """
    mock_requests_get.return_value = mock_response

    get_staff_data.cache_clear()

    result = get_staff_data()

    assert result == [
        {"name": "Person A", "title": "Title A"},
        {"name": "Person B", "title": "Title B"},
    ]


@patch("requests.get")
def test_get_staff_data_request_exception(mock_requests_get, caplog):
    """Test get_staff_data function with request exception."""
    mock_requests_get.side_effect = RequestException("Connection error")

    get_staff_data.cache_clear()

    result = get_staff_data()

    assert result is None
    assert "Unable to parse OWASP staff data file" in caplog.text


@patch("requests.get")
def test_get_staff_data_yaml_exception(mock_requests_get, caplog):
    """Test get_staff_data function with YAML parsing exception."""
    mock_response = MagicMock()
    mock_response.text = "invalid: yaml: content:"
    mock_requests_get.return_value = mock_response

    get_staff_data.cache_clear()

    with patch("yaml.safe_load", side_effect=yaml.scanner.ScannerError):
        result = get_staff_data()

    assert result is None
    assert "Unable to parse OWASP staff data file" in caplog.text


@patch("apps.owasp.models.event.Event.objects.filter")
def test_get_events_data_success(mock_filter):
    """Test get_events_data function with successful query."""
    mock_queryset = MagicMock()
    mock_ordered = MagicMock()
    mock_filter.return_value = mock_queryset
    mock_queryset.order_by.return_value = mock_ordered

    result = get_events_data()

    assert result is mock_ordered
    mock_queryset.order_by.assert_called_once_with("start_date")


@patch("apps.owasp.models.event.Event.objects.filter")
def test_get_events_data_exception(mock_filter, caplog):
    """Test get_events_data function with exception."""
    mock_filter.side_effect = Exception(database_error)

    result = get_events_data()

    assert result is None
    assert "Failed to fetch events data via database" in caplog.text
    assert database_error in caplog.text


@patch("apps.owasp.models.sponsor.Sponsor.objects.all")
def test_get_sponsors_data_success(mock_all):
    """Test get_sponsors_data function with successful query."""
    mock_queryset = MagicMock()
    mock_all.return_value = mock_queryset
    mock_limited = MagicMock()
    mock_queryset.__getitem__.return_value = mock_limited

    result = get_sponsors_data()

    assert result is mock_limited
    mock_queryset.__getitem__.assert_called_once_with(slice(None, 10))

    result_limited = get_sponsors_data(limit=5)
    assert result_limited is mock_limited
    mock_queryset.__getitem__.assert_called_with(slice(None, 5))


@patch("apps.owasp.models.sponsor.Sponsor.objects.all")
def test_get_sponsors_data_exception(mock_all, caplog):
    """Test get_sponsors_data function with exception."""
    mock_all.side_effect = Exception(database_error)

    result = get_sponsors_data()

    assert result is None
    assert "Failed to fetch sponsors data via database" in caplog.text
    assert database_error in caplog.text


@patch("apps.owasp.models.sponsor.Sponsor.objects.all")
def test_get_sponsors_data_with_different_limits(mock_all):
    """Test get_sponsors_data function with different limits."""
    mock_queryset = MagicMock()
    mock_all.return_value = mock_queryset
    mock_limited = MagicMock()
    mock_queryset.__getitem__.return_value = mock_limited

    default_limit = get_sponsors_data()
    assert default_limit is mock_limited
    mock_queryset.__getitem__.assert_called_with(slice(None, 10))

    custom_limit = get_sponsors_data(limit=5)
    assert custom_limit is mock_limited
    mock_queryset.__getitem__.assert_called_with(slice(None, 5))

    zero_limit = get_sponsors_data(limit=0)
    assert zero_limit is mock_limited
    mock_queryset.__getitem__.assert_called_with(slice(None, 0))


@patch("apps.owasp.models.event.Event.objects.filter")
def test_get_events_data_empty_result(mock_filter):
    """Test get_events_data function with empty result."""
    mock_queryset = MagicMock()
    mock_ordered = []
    mock_filter.return_value = mock_queryset
    mock_queryset.order_by.return_value = mock_ordered

    result = get_events_data()

    assert result == []
    mock_queryset.order_by.assert_called_once_with("start_date")


def test_strip_markdown_edge_cases():
    """Test strip_markdown function with edge cases."""
    assert strip_markdown("") == ""
    assert strip_markdown("*") == ""
    assert strip_markdown("**") == ""
    assert strip_markdown("***") == ""
    assert strip_markdown("<https://example.com|>") == "<https://example.com|>"
    assert strip_markdown("Text *with* multiple *asterisks*") == "Text with multiple asterisks"
    assert strip_markdown("Text**with**adjacent**asterisks") == "Textwithadjacentasterisks"
    assert strip_markdown("No formatting just text") == "No formatting just text"
    assert (
        strip_markdown("Mixed *bold* and <https://example.com|link>")
        == "Mixed bold and link (https://example.com)"
    )


"""Test suite for slack utility functions."""


class TestSlackUtils:
    def test_get_text_empty_blocks(self):
        assert get_text([]) == ""

    def test_get_text_section_with_mrkdwn(self):
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Hello *world*"}}]
        assert get_text(blocks) == "Hello world"

    def test_get_text_section_without_mrkdwn(self):
        blocks = [{"type": "section", "text": {"type": "plain_text", "text": "Hello world"}}]
        assert get_text(blocks) == ""

    def test_get_text_section_with_fields(self):
        blocks = [
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": "Field 1: *value*"},
                    {"type": "mrkdwn", "text": "Field 2: *value*"},
                ],
            }
        ]
        assert get_text(blocks) == "Field 1: value\nField 2: value"

    def test_get_text_section_with_non_mrkdwn_fields(self):
        blocks = [
            {"type": "section", "fields": [{"type": "plain_text", "text": "Field 1: value"}]}
        ]
        assert get_text(blocks) == ""

    def test_get_text_divider(self):
        blocks = [{"type": "divider"}]
        assert get_text(blocks) == "---"

    def test_get_text_context(self):
        blocks = [
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": "Context 1: *value*"},
                    {"type": "mrkdwn", "text": "Context 2: *value*"},
                ],
            }
        ]
        assert get_text(blocks) == "Context 1: value\nContext 2: value"

    def test_get_text_context_non_mrkdwn(self):
        blocks = [
            {
                "type": "context",
                "elements": [{"type": "image", "image_url": "https://example.com/img.png"}],
            }
        ]
        assert get_text(blocks) == ""

    def test_get_text_actions(self):
        blocks = [
            {
                "type": "actions",
                "elements": [
                    {"type": "button", "text": {"type": "plain_text", "text": "Button 1"}},
                    {"type": "button", "text": {"type": "plain_text", "text": "Button 2"}},
                ],
            }
        ]
        assert get_text(blocks) == "Button 1\nButton 2"

    def test_get_text_actions_non_button(self):
        blocks = [
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "datepicker",
                        "placeholder": {"type": "plain_text", "text": "Select date"},
                    }
                ],
            }
        ]
        assert get_text(blocks) == ""

    def test_get_text_image(self):
        blocks = [
            {
                "type": "image",
                "image_url": "https://example.com/img.png",
                "alt_text": "Example image",
            }
        ]
        assert get_text(blocks) == "Image: https://example.com/img.png"

        blocks = [{"type": "image"}]
        assert get_text(blocks) == "Image:"

    def test_get_text_header(self):
        blocks = [{"type": "header", "text": {"type": "plain_text", "text": "Header text"}}]
        assert get_text(blocks) == "Header text"

        blocks = [{"type": "header", "text": {"type": "mrkdwn", "text": "Header *text*"}}]
        assert get_text(blocks) == ""

    def test_get_text_unknown_block_type(self):
        blocks = [{"type": "unknown_type"}]
        assert get_text(blocks) == ""

    def test_strip_markdown(self):
        assert strip_markdown("<https://example.com|Example>") == "Example (https://example.com)"
        assert strip_markdown("*Bold text*") == "Bold text"
        assert strip_markdown("_Italic text_") == "_Italic text_"
        assert strip_markdown("<https://example.com>") == "<https://example.com>"
        assert strip_markdown("Plain text") == "Plain text"
        assert (
            strip_markdown("<https://example.com/path?query=value|Link with query>")
            == "Link with query (https://example.com/path?query=value)"
        )
