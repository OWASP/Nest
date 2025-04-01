from unittest.mock import patch

import pytest

from apps.slack.common.handlers.chapters import get_blocks
from apps.slack.common.presentation import EntityPresentation

EXPECTED_ELEMENTS_COUNT = 2
EXPECTED_BLOCK_COUNT = 4


class TestChapterHandler:
    @pytest.fixture()
    def mock_chapter_data(self):
        return {
            "hits": [
                {
                    "idx_name": "Test Chapter",
                    "idx_summary": "This is a test chapter summary",
                    "idx_url": "https://example.com/chapter",
                    "idx_country": "Country",
                    "idx_region": "Region",
                    "idx_suggested_location": "City, Country",
                    "idx_leaders": ["John Doe", "Jane Smith"],
                    "idx_updated_at": "1704067200",  # 2024-01-01
                }
            ],
            "nbPages": 2,
        }

    @pytest.fixture()
    def mock_empty_chapter_data(self):
        return {
            "hits": [],
            "nbPages": 0,
        }

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        with patch("apps.owasp.api.search.chapter.get_chapters") as mock_get_chapters, patch(
            "apps.owasp.models.chapter.Chapter"
        ) as mock_chapter_model:
            mock_chapter_model.active_chapters_count.return_value = 42
            yield {"get_chapters": mock_get_chapters, "chapter_model": mock_chapter_model}

    def test_get_blocks_with_results(self, setup_mocks, mock_chapter_data):
        setup_mocks["get_chapters"].return_value = mock_chapter_data

        blocks = get_blocks(search_query="test")

        assert "OWASP chapters that I found for" in blocks[0]["text"]["text"]
        assert "Test Chapter" in blocks[1]["text"]["text"]
        assert "City, Country" in blocks[1]["text"]["text"]
        assert "Leader" in blocks[1]["text"]["text"]

    def test_get_blocks_no_results(self, setup_mocks, mock_empty_chapter_data):
        setup_mocks["get_chapters"].return_value = mock_empty_chapter_data

        blocks = get_blocks(search_query="nonexistent")

        assert len(blocks) == 1
        assert "No chapters found for" in blocks[0]["text"]["text"]

    def test_get_blocks_without_search_query(self, setup_mocks, mock_chapter_data):
        setup_mocks["get_chapters"].return_value = mock_chapter_data

        blocks = get_blocks()

        assert "OWASP chapters:" in blocks[0]["text"]["text"]

    def test_get_blocks_no_results_without_query(self, setup_mocks, mock_empty_chapter_data):
        setup_mocks["get_chapters"].return_value = mock_empty_chapter_data

        blocks = get_blocks()

        assert "No chapters found" in blocks[0]["text"]["text"]
        assert "`" not in blocks[0]["text"]["text"]

    def test_feedback_message(self, setup_mocks, mock_chapter_data):
        setup_mocks["get_chapters"].return_value = mock_chapter_data
        presentation = EntityPresentation(include_feedback=True)

        blocks = get_blocks(presentation=presentation)

        assert "Extended search over 42 OWASP chapters" in blocks[-1]["text"]["text"]

    def test_pagination(self, setup_mocks, mock_chapter_data):
        mock_chapter_data["nbPages"] = 3
        setup_mocks["get_chapters"].return_value = mock_chapter_data
        presentation = EntityPresentation(include_pagination=True)

        with patch(
            "apps.slack.common.handlers.chapters.get_pagination_buttons"
        ) as mock_pagination:
            mock_pagination.return_value = [
                {"type": "button", "text": {"type": "plain_text", "text": "Next"}}
            ]
            blocks = get_blocks(page=1, presentation=presentation)
            assert mock_pagination.called
            assert blocks[-1]["type"] == "actions"

            mock_pagination.return_value = [
                {"type": "button", "text": {"type": "plain_text", "text": "Previous"}},
                {"type": "button", "text": {"type": "plain_text", "text": "Next"}},
            ]
            blocks = get_blocks(page=2, presentation=presentation)
            assert len(blocks[-1]["elements"]) == EXPECTED_ELEMENTS_COUNT
            assert mock_pagination.call_count == EXPECTED_ELEMENTS_COUNT

    def test_location_fallback(self, setup_mocks, mock_chapter_data):
        with patch("apps.slack.common.handlers.chapters.get_pagination_buttons", return_value=[]):
            setup_mocks["get_chapters"].return_value = mock_chapter_data
            blocks = get_blocks()
            assert "City, Country" in blocks[1]["text"]["text"]

            mock_chapter_data["hits"][0]["idx_suggested_location"] = None
            setup_mocks["get_chapters"].return_value = mock_chapter_data

            blocks = get_blocks()
            assert "Country" in blocks[1]["text"]["text"]

    def test_leaders_singular_plural(self, setup_mocks, mock_chapter_data):
        with patch("apps.slack.common.handlers.chapters.get_pagination_buttons", return_value=[]):
            presentation = EntityPresentation(include_metadata=True)
            setup_mocks["get_chapters"].return_value = mock_chapter_data
            blocks = get_blocks(presentation=presentation)
            assert "Leaders: John Doe, Jane Smith" in blocks[1]["text"]["text"]

            mock_chapter_data["hits"][0]["idx_leaders"] = ["John Doe"]
            setup_mocks["get_chapters"].return_value = mock_chapter_data

            blocks = get_blocks(presentation=presentation)
            assert "Leader: John Doe" in blocks[1]["text"]["text"]

    def test_no_leaders_display_when_metadata_disabled(self, setup_mocks, mock_chapter_data):
        with patch("apps.slack.common.handlers.chapters.get_pagination_buttons", return_value=[]):
            presentation = EntityPresentation(include_metadata=False)
            setup_mocks["get_chapters"].return_value = mock_chapter_data
            blocks = get_blocks(presentation=presentation)
            assert "Leader" not in blocks[1]["text"]["text"]

    def test_pagination_empty(self, setup_mocks, mock_chapter_data):
        mock_chapter_data["nbPages"] = 1
        setup_mocks["get_chapters"].return_value = mock_chapter_data
        presentation = EntityPresentation(include_pagination=True)

        with patch("apps.slack.common.handlers.chapters.get_pagination_buttons", return_value=[]):
            blocks = get_blocks(page=1, presentation=presentation)
            assert all(block["type"] != "actions" for block in blocks)

    def test_pagination_edge_case(self, setup_mocks, mock_chapter_data):
        mock_chapter_data["nbPages"] = 2
        setup_mocks["get_chapters"].return_value = mock_chapter_data
        presentation = EntityPresentation(include_pagination=True)

        with patch(
            "apps.slack.common.handlers.chapters.get_pagination_buttons"
        ) as mock_pagination:
            mock_pagination.return_value = None
            blocks = get_blocks(page=2, presentation=presentation)
            assert all(block["type"] != "actions" for block in blocks)
            assert mock_pagination.called

    def test_none_pagination_return_value(self, setup_mocks, mock_chapter_data):
        """Test handling when pagination buttons function returns None."""
        mock_chapter_data["nbPages"] = 2
        setup_mocks["get_chapters"].return_value = mock_chapter_data
        presentation = EntityPresentation(include_pagination=True)

        with patch(
            "apps.slack.common.handlers.chapters.get_pagination_buttons"
        ) as mock_pagination:
            mock_pagination.return_value = None
            blocks = get_blocks(page=1, presentation=presentation)

            assert all(block.get("type") != "actions" for block in blocks)
            assert mock_pagination.called

    def test_empty_pagination_list(self, setup_mocks, mock_chapter_data):
        """Test handling when pagination buttons function returns an empty list."""
        mock_chapter_data["nbPages"] = 2
        setup_mocks["get_chapters"].return_value = mock_chapter_data
        presentation = EntityPresentation(include_pagination=True)

        with patch(
            "apps.slack.common.handlers.chapters.get_pagination_buttons"
        ) as mock_pagination:
            mock_pagination.return_value = []
            blocks = get_blocks(page=1, presentation=presentation)

            assert all(block.get("type") != "actions" for block in blocks)
            assert mock_pagination.called

    def test_feedback_and_pagination_together(self, setup_mocks, mock_chapter_data):
        mock_chapter_data["nbPages"] = 3
        setup_mocks["get_chapters"].return_value = mock_chapter_data

        presentation = EntityPresentation(include_feedback=True, include_pagination=True)

        with patch(
            "apps.slack.common.handlers.chapters.get_pagination_buttons"
        ) as mock_pagination:
            mock_pagination.return_value = [
                {"type": "button", "text": {"type": "plain_text", "text": "Next"}}
            ]

            blocks = get_blocks(page=1, search_query="test_query", presentation=presentation)

            feedback_block = blocks[-2]
            assert "Extended search over 42 OWASP chapters" in feedback_block["text"]["text"]
            assert "test_query" in feedback_block["text"]["text"]
            assert "share feedback" in feedback_block["text"]["text"]

            pagination_block = blocks[-1]
            assert pagination_block["type"] == "actions"
            assert len(pagination_block["elements"]) == 1

            assert len(blocks) >= EXPECTED_BLOCK_COUNT
