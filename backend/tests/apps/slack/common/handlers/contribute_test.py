"""Tests for contribute handler functionality."""

from unittest.mock import patch

import pytest

from apps.slack.common.handlers.contribute import get_blocks
from apps.slack.common.presentation import EntityPresentation


class TestContributeHandler:
    @pytest.fixture
    def mock_contribute_data(self):
        return {
            "hits": [
                {
                    "idx_title": "Test Issue",
                    "idx_project_name": "OWASP Test Project",
                    "idx_project_url": "https://example.com/project",
                    "idx_summary": "This is a test issue summary",
                    "idx_url": "https://example.com/issue",
                }
            ],
            "nbPages": 2,
        }

    @pytest.fixture
    def mock_empty_contribute_data(self):
        return {
            "hits": [],
            "nbPages": 0,
        }

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        with (
            patch("apps.owasp.index.search.issue.get_issues") as mock_get_issues,
            patch("apps.github.models.issue.Issue") as mock_issue_model,
        ):
            mock_issue_model.open_issues_count.return_value = 100
            yield {"get_issues": mock_get_issues, "issue_model": mock_issue_model}

    def test_get_blocks_with_results(self, setup_mocks, mock_contribute_data):
        setup_mocks["get_issues"].return_value = mock_contribute_data

        blocks = get_blocks(search_query="test")

        assert len(blocks) >= 1
        assert "Test Issue" in blocks[0]["text"]["text"]
        assert "OWASP Test Project" in blocks[0]["text"]["text"]
        assert "This is a test issue summary" in blocks[0]["text"]["text"]

    def test_get_blocks_no_results(self, setup_mocks, mock_empty_contribute_data):
        setup_mocks["get_issues"].return_value = mock_empty_contribute_data

        blocks = get_blocks(search_query="nonexistent")

        assert len(blocks) == 1
        assert "No issues found for" in blocks[0]["text"]["text"]

    def test_get_blocks_text_truncation(self, setup_mocks):
        long_title = "Very Long Issue Title That Should Be Truncated"
        mock_data = {
            "hits": [
                {
                    "idx_title": long_title,
                    "idx_project_name": "Project",
                    "idx_project_url": "https://example.com/project",
                    "idx_summary": "Test Summary",
                    "idx_url": "https://example.com",
                }
            ],
            "nbPages": 1,
        }
        setup_mocks["get_issues"].return_value = mock_data

        presentation = EntityPresentation(name_truncation=20)
        blocks = get_blocks(presentation=presentation)

        assert long_title[:17] + "..." in blocks[0]["text"]["text"]

    def test_get_blocks_with_feedback(self, setup_mocks, mock_contribute_data):
        setup_mocks["get_issues"].return_value = mock_contribute_data
        presentation = EntityPresentation(include_feedback=True)

        blocks = get_blocks(presentation=presentation)

        assert "Extended search over 100 open issues" in blocks[-1]["text"]["text"]

    def test_get_blocks_without_feedback(self, setup_mocks, mock_contribute_data):
        setup_mocks["get_issues"].return_value = mock_contribute_data
        presentation = EntityPresentation(include_feedback=False)

        blocks = get_blocks(presentation=presentation)

        assert not any("Extended search" in str(block) for block in blocks)

    def test_get_blocks_with_pagination_on_page_2(self, setup_mocks, mock_contribute_data):
        """Test that pagination buttons are added on page 2."""
        setup_mocks["get_issues"].return_value = mock_contribute_data
        presentation = EntityPresentation(include_pagination=True)

        blocks = get_blocks(page=2, presentation=presentation)

        assert any(block.get("type") == "actions" for block in blocks)

    def test_get_blocks_without_pagination_buttons(self, setup_mocks, mock_contribute_data):
        """Test that no pagination buttons are added when include_pagination is False."""
        setup_mocks["get_issues"].return_value = mock_contribute_data
        presentation = EntityPresentation(include_pagination=False)

        blocks = get_blocks(page=1, presentation=presentation)

        assert not any(block.get("type") == "actions" for block in blocks)

    def test_pagination_offset(self, setup_mocks, mock_contribute_data):
        setup_mocks["get_issues"].return_value = mock_contribute_data
        page = 2
        limit = 10

        blocks = get_blocks(page=page, limit=limit)

        assert "11. " in blocks[0]["text"]["text"]

    def test_get_blocks_no_search_query(self, setup_mocks, mock_contribute_data):
        """Test get_blocks without search query."""
        setup_mocks["get_issues"].return_value = mock_contribute_data

        blocks = get_blocks(search_query="")

        assert "No issues found" not in str(blocks)
        assert "Test Issue" in blocks[0]["text"]["text"]
