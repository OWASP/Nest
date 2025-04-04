from unittest.mock import Mock
from urllib.parse import urljoin

import pytest

from apps.common.constants import OWASP_NEWS_URL
from apps.slack.utils import (
    escape,
    get_gsoc_projects,
    get_news_data,
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
def test_process_mrkdwn(input_text, expected_output):
    """Test the _process_mrkdwn function."""
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
