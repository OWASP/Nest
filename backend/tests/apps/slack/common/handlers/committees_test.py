from unittest.mock import patch

import pytest

from apps.slack.common.handlers.committees import get_blocks
from apps.slack.common.presentation import EntityPresentation


class TestCommitteeHandler:
    @pytest.fixture
    def mock_committee_data(self):
        return {
            "hits": [
                {
                    "idx_name": "Test Committee",
                    "idx_leaders": ["John Doe", "Jane Smith"],
                    "idx_summary": "This is a test committee summary",
                    "idx_url": "https://example.com/committee",
                }
            ],
            "nbPages": 2,
        }

    @pytest.fixture
    def mock_empty_committee_data(self):
        return {
            "hits": [],
            "nbPages": 0,
        }

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        with (
            patch("apps.owasp.index.search.committee.get_committees") as mock_get_committees,
            patch("apps.owasp.models.committee.Committee") as mock_committee_model,
        ):
            mock_committee_model.active_committees_count.return_value = 15
            yield {"get_committees": mock_get_committees, "committee_model": mock_committee_model}

    def test_get_blocks_with_results(self, setup_mocks, mock_committee_data):
        setup_mocks["get_committees"].return_value = mock_committee_data

        blocks = get_blocks(search_query="test")

        assert "OWASP committees that I found for" in blocks[0]["text"]["text"]
        assert "Test Committee" in blocks[1]["text"]["text"]
        assert "Leaders: John Doe, Jane Smith" in blocks[1]["text"]["text"]
        assert "This is a test committee summary" in blocks[1]["text"]["text"]

    def test_get_blocks_no_results(self, setup_mocks, mock_empty_committee_data):
        setup_mocks["get_committees"].return_value = mock_empty_committee_data

        blocks = get_blocks(search_query="nonexistent")

        assert len(blocks) == 1
        assert "No committees found for" in blocks[0]["text"]["text"]

    def test_get_blocks_without_metadata(self, setup_mocks, mock_committee_data):
        setup_mocks["get_committees"].return_value = mock_committee_data
        presentation = EntityPresentation(include_metadata=False)

        blocks = get_blocks(presentation=presentation)

        assert "Leaders:" not in blocks[1]["text"]["text"]

    def test_get_blocks_single_leader(self, setup_mocks):
        mock_data = {
            "hits": [
                {
                    "idx_name": "Single Leader Committee",
                    "idx_leaders": ["John Doe"],
                    "idx_summary": "Test Summary",
                    "idx_url": "https://example.com",
                }
            ],
            "nbPages": 1,
        }
        setup_mocks["get_committees"].return_value = mock_data
        presentation = EntityPresentation(include_metadata=True)

        blocks = get_blocks(presentation=presentation)

        assert "Leader: John Doe" in blocks[1]["text"]["text"]  # Singular form
        assert "Leaders:" not in blocks[1]["text"]["text"]  # Not plural

    def test_get_blocks_text_truncation(self, setup_mocks):
        long_name = "Very Long Committee Name That Should Be Truncated"
        mock_data = {
            "hits": [
                {
                    "idx_name": long_name,
                    "idx_summary": "Test Summary",
                    "idx_url": "https://example.com",
                    "idx_leaders": [],
                }
            ],
            "nbPages": 1,
        }
        setup_mocks["get_committees"].return_value = mock_data

        presentation = EntityPresentation(name_truncation=20)
        blocks = get_blocks(presentation=presentation)

        assert long_name[:17] + "..." in blocks[1]["text"]["text"]

    def test_feedback_message(self, setup_mocks, mock_committee_data):
        setup_mocks["get_committees"].return_value = mock_committee_data
        presentation = EntityPresentation(include_feedback=True)

        blocks = get_blocks(presentation=presentation)

        assert "Extended search over 15 OWASP committees" in blocks[-1]["text"]["text"]

    def test_search_query_escaping(self, setup_mocks, mock_committee_data):
        setup_mocks["get_committees"].return_value = mock_committee_data
        dangerous_query = "test & <script>"

        blocks = get_blocks(search_query=dangerous_query)

        assert "&amp;" in blocks[0]["text"]["text"]
        assert "&lt;script&gt;" in blocks[0]["text"]["text"]

    def test_committee_without_leaders(self, setup_mocks):
        mock_data = {
            "hits": [
                {
                    "idx_name": "No Leaders Committee",
                    "idx_summary": "Test Summary",
                    "idx_url": "https://example.com",
                }
            ],
            "nbPages": 1,
        }
        setup_mocks["get_committees"].return_value = mock_data
        presentation = EntityPresentation(include_metadata=True)

        blocks = get_blocks(presentation=presentation)

        assert "Leaders:" not in blocks[1]["text"]["text"]

    def test_pagination_offset(self, setup_mocks, mock_committee_data):
        setup_mocks["get_committees"].return_value = mock_committee_data
        page = 2
        limit = 10

        blocks = get_blocks(page=page, limit=limit)

        # First item should be numbered 11 (offset + 1)
        assert "11. " in blocks[1]["text"]["text"]

    def test_get_blocks_no_search_query(self, setup_mocks, mock_committee_data):
        """Test get_blocks without search query."""
        setup_mocks["get_committees"].return_value = mock_committee_data

        blocks = get_blocks(search_query="")

        # Should not include search query text
        assert "OWASP committees:" in blocks[0]["text"]["text"]
        assert "Test Committee" in blocks[1]["text"]["text"]

    def test_get_blocks_without_pagination_buttons(self, setup_mocks, mock_committee_data):
        """Test that no pagination buttons are added when include_pagination is False."""
        setup_mocks["get_committees"].return_value = mock_committee_data
        presentation = EntityPresentation(include_pagination=False)

        blocks = get_blocks(page=1, presentation=presentation)

        # Should not have actions block
        assert not any(block.get("type") == "actions" for block in blocks)

    def test_get_blocks_with_pagination_on_page_2(self, setup_mocks, mock_committee_data):
        """Test that pagination buttons are added on page 2."""
        setup_mocks["get_committees"].return_value = mock_committee_data
        presentation = EntityPresentation(include_pagination=True)

        blocks = get_blocks(page=2, presentation=presentation)

        # Should have actions block with pagination buttons on page 2
        assert any(block.get("type") == "actions" for block in blocks)

    def test_get_blocks_without_pagination_buttons(self, setup_mocks, mock_committee_data):
        """Test that no pagination buttons are added when include_pagination is False."""
        setup_mocks["get_committees"].return_value = mock_committee_data
        presentation = EntityPresentation(include_pagination=False)

        blocks = get_blocks(page=1, presentation=presentation)

        # Should not have actions block
        assert not any(block.get("type") == "actions" for block in blocks)
