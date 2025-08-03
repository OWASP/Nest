from unittest.mock import patch

import pytest

from apps.slack.common.handlers.chapters import get_blocks
from apps.slack.common.presentation import EntityPresentation


class TestChapterHandler:
    @pytest.fixture
    def mock_chapter_data(self):
        return {
            "hits": [
                {
                    "idx_name": "Test Chapter",
                    "idx_country": "United States",
                    "idx_suggested_location": "New York",
                    "idx_leaders": ["John Doe", "Jane Smith"],
                    "idx_summary": "This is a test chapter summary",
                    "idx_url": "https://example.com/chapter",
                }
            ],
            "nbPages": 2,
        }

    @pytest.fixture
    def mock_empty_chapter_data(self):
        return {
            "hits": [],
            "nbPages": 0,
        }

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        with (
            patch("apps.owasp.index.search.chapter.get_chapters") as mock_get_chapters,
            patch("apps.owasp.models.chapter.Chapter") as mock_chapter_model,
        ):
            mock_chapter_model.active_chapters_count.return_value = 42
            yield {"get_chapters": mock_get_chapters, "chapter_model": mock_chapter_model}

    def test_get_blocks_with_results(self, setup_mocks, mock_chapter_data):
        setup_mocks["get_chapters"].return_value = mock_chapter_data

        blocks = get_blocks(search_query="test")

        assert "OWASP chapters that I found for" in blocks[0]["text"]["text"]
        assert "Test Chapter" in blocks[1]["text"]["text"]
        assert "New York" in blocks[1]["text"]["text"]
        assert "John Doe, Jane Smith" in blocks[1]["text"]["text"]

    def test_get_blocks_no_results(self, setup_mocks, mock_empty_chapter_data):
        setup_mocks["get_chapters"].return_value = mock_empty_chapter_data

        blocks = get_blocks(search_query="nonexistent")

        assert len(blocks) == 1
        assert "No chapters found for" in blocks[0]["text"]["text"]

    def test_get_blocks_pagination(self, setup_mocks, mock_chapter_data):
        setup_mocks["get_chapters"].return_value = mock_chapter_data
        presentation = EntityPresentation(include_pagination=True)

        blocks = get_blocks(page=1, presentation=presentation)

        assert blocks[-1]["type"] == "section"

    def test_get_blocks_text_truncation(self, setup_mocks):
        long_name = "Very Long Chapter Name That Should Be Truncated"
        mock_data = {
            "hits": [
                {
                    "idx_name": long_name,
                    "idx_country": "Test Country",
                    "idx_summary": "Test Summary",
                    "idx_suggested_location": "Test Location",
                    "idx_url": "https://example.com",
                }
            ],
            "nbPages": 1,
        }
        setup_mocks["get_chapters"].return_value = mock_data

        presentation = EntityPresentation(name_truncation=20)
        blocks = get_blocks(presentation=presentation)

        assert long_name[:17] + "..." in blocks[1]["text"]["text"]

    def test_feedback_message(self, setup_mocks, mock_chapter_data):
        setup_mocks["get_chapters"].return_value = mock_chapter_data
        presentation = EntityPresentation(include_feedback=True)

        blocks = get_blocks(presentation=presentation)

        assert "Extended search over 42 OWASP chapters" in blocks[-1]["text"]["text"]
