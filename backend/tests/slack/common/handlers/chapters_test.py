from unittest.mock import patch

import pytest

from apps.slack.common.presentation import EntityPresentation
from apps.slack.handlers.chapters import chapters_blocks


class TestChaptersHandler:
    @pytest.fixture()
    def mock_chapter(self):
        return {
            "idx_name": "Test Chapter",
            "idx_summary": "Test Chapter Summary",
            "idx_url": "http://example.com/chapter/1",
            "idx_country": "Test Country",
            "idx_suggested_location": "Test Location",
            "idx_leaders": ["Leader 1", "Leader 2"],
            "idx_region": "Test Region",
            "idx_updated_at": "2024-01-01T00:00:00Z",
        }

    @pytest.mark.parametrize(
        ("search_query", "has_results", "expected_message"),
        [
            ("python", True, "OWASP chapters that I found for"),
            ("python", False, "No chapters found for"),
            ("", True, "OWASP chapters:"),
            ("", False, "No chapters found"),
        ],
    )
    @patch("apps.owasp.api.search.chapter.get_chapters")
    @patch("apps.owasp.models.chapter.Chapter.active_chapters_count")
    def test_chapters_blocks_results(
        self,
        mock_active_chapters_count,
        mock_get_chapters,
        search_query,
        has_results,
        expected_message,
        mock_chapter,
    ):
        mock_get_chapters.return_value = {"hits": [mock_chapter] if has_results else []}
        mock_active_chapters_count.return_value = 42

        blocks = chapters_blocks(search_query=search_query)

        assert any(expected_message in str(block) for block in blocks)
        if has_results:
            assert any(mock_chapter["idx_name"] in str(block) for block in blocks)

    @pytest.mark.parametrize(
        ("presentation_params", "expected_content"),
        [
            ({"include_metadata": True}, ["Leader 1", "Leader 2"]),
            ({"include_metadata": False}, []),
            ({"name_truncation": 5}, ["Test..."]),
        ],
    )
    @patch("apps.owasp.api.search.chapter.get_chapters")
    def test_chapters_blocks_presentation(
        self,
        mock_get_chapters,
        presentation_params,
        expected_content,
        mock_chapter,
    ):
        mock_get_chapters.return_value = {"hits": [mock_chapter]}
        presentation = EntityPresentation(**presentation_params)

        blocks = chapters_blocks(presentation=presentation)

        for content in expected_content:
            assert any(content in str(block) for block in blocks)
