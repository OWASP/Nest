from unittest.mock import patch

import pytest
from django.utils.text import Truncator

from apps.slack.common.handlers import (
    EntityPresentation,
    chapters_blocks,
    committees_blocks,
    projects_blocks,
)
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE

DEFAULT_NAME_TRUNCATION = 80
DEFAULT_SUMMARY_TRUNCATION = 300
CUSTOM_NAME_TRUNCATION = 50
CUSTOM_SUMMARY_TRUNCATION = 200


class TestEntityPresentation:
    def test_default_values(self):
        presentation = EntityPresentation()
        assert presentation.name_truncation == DEFAULT_NAME_TRUNCATION
        assert presentation.summary_truncation == DEFAULT_SUMMARY_TRUNCATION
        assert presentation.include_feedback is True
        assert presentation.include_timestamps is True
        assert presentation.include_metadata is True

    def test_custom_values(self):
        presentation = EntityPresentation(
            name_truncation=50,
            summary_truncation=200,
            include_feedback=False,
            include_timestamps=False,
            include_metadata=False,
        )
        assert presentation.name_truncation == CUSTOM_NAME_TRUNCATION
        assert presentation.summary_truncation == CUSTOM_SUMMARY_TRUNCATION
        assert presentation.include_feedback is False
        assert presentation.include_timestamps is False
        assert presentation.include_metadata is False


class TestChaptersBlocks:
    @pytest.fixture()
    def mock_chapter(self):
        return {
            "idx_name": "Test Chapter",
            "idx_suggested_location": "Test Location",
            "idx_country": "Test Country",
            "idx_leaders": ["Leader A", "Leader B"],
            "idx_summary": "Test Summary",
            "idx_url": "http://example.com",
            "idx_updated_at": "2024-01-01T00:00:00Z",
        }

    @pytest.mark.parametrize(
        ("search_query", "has_results", "expected_text"),
        [
            ("test", True, "OWASP chapters that I found for"),
            ("", True, "OWASP chapters:"),
            ("test", False, "No chapters found for"),
            ("", False, "No chapters found"),
        ],
    )
    @patch("apps.owasp.api.search.chapter.get_chapters")
    @patch("apps.owasp.models.chapter.Chapter.active_chapters_count")
    def test_chapters_blocks(
        self,
        mock_active_count,
        mock_get_chapters,
        search_query,
        has_results,
        expected_text,
        mock_chapter,
    ):
        mock_get_chapters.return_value = {"hits": [mock_chapter] if has_results else []}
        mock_active_count.return_value = 42

        blocks = chapters_blocks(search_query=search_query)

        assert len(blocks) > 0
        assert any(expected_text in str(block) for block in blocks)

        if has_results:
            assert any(mock_chapter["idx_name"] in str(block) for block in blocks)
            assert any(mock_chapter["idx_summary"] in str(block) for block in blocks)

    @patch("apps.owasp.api.search.chapter.get_chapters")
    @patch("apps.owasp.models.chapter.Chapter.active_chapters_count")
    def test_chapters_blocks_presentation(
        self, mock_active_count, mock_get_chapters, mock_chapter
    ):
        mock_get_chapters.return_value = {"hits": [mock_chapter]}
        mock_active_count.return_value = 42

        presentation = EntityPresentation(
            name_truncation=10,
            summary_truncation=20,
            include_feedback=False,
            include_timestamps=False,
            include_metadata=False,
        )

        blocks = chapters_blocks(presentation=presentation)

        truncated_name = Truncator(mock_chapter["idx_name"]).chars(10, truncate="...")
        truncated_summary = Truncator(mock_chapter["idx_summary"]).chars(20, truncate="...")

        assert any(truncated_name in str(block) for block in blocks)
        assert any(truncated_summary in str(block) for block in blocks)
        assert not any(FEEDBACK_CHANNEL_MESSAGE in str(block) for block in blocks)


class TestProjectsBlocks:
    @pytest.fixture()
    def mock_project(self):
        return {
            "idx_name": "Test Project",
            "idx_summary": "Test Summary",
            "idx_url": "http://example.com",
            "idx_updated_at": "2024-01-01T00:00:00Z",
            "idx_contributors_count": 10,
            "idx_forks_count": 5,
            "idx_stars_count": 100,
            "idx_leaders": ["Leader A"],
            "idx_level": "Flagship",
        }

    @pytest.mark.parametrize(
        ("search_query", "has_results", "expected_text"),
        [
            ("test", True, "OWASP projects that I found for"),
            ("", True, "OWASP projects:"),
            ("test", False, "No projects found for"),
            ("", False, "No projects found"),
        ],
    )
    @patch("apps.owasp.api.search.project.get_projects")
    @patch("apps.owasp.models.project.Project.active_projects_count")
    def test_projects_blocks(
        self,
        mock_active_count,
        mock_get_projects,
        search_query,
        has_results,
        expected_text,
        mock_project,
    ):
        mock_get_projects.return_value = {"hits": [mock_project] if has_results else []}
        mock_active_count.return_value = 42

        blocks = projects_blocks(search_query=search_query)

        assert len(blocks) > 0
        assert any(expected_text in str(block) for block in blocks)

        if has_results:
            assert any(mock_project["idx_name"] in str(block) for block in blocks)
            assert any(
                str(mock_project["idx_contributors_count"]) in str(block) for block in blocks
            )


class TestCommitteesBlocks:
    @pytest.fixture()
    def mock_committee(self):
        return {
            "idx_name": "Test Committee",
            "idx_summary": "Test Summary",
            "idx_url": "http://example.com",
            "idx_leaders": ["Leader A", "Leader B"],
        }

    @pytest.mark.parametrize(
        ("search_query", "has_results", "expected_text"),
        [
            ("test", True, "OWASP committees that I found for"),
            ("", True, "OWASP committees:"),
            ("test", False, "No committees found for"),
            ("", False, "No committees found"),
        ],
    )
    @patch("apps.owasp.api.search.committee.get_committees")
    @patch("apps.owasp.models.committee.Committee.active_committees_count")
    def test_committees_blocks(
        self,
        mock_active_count,
        mock_get_committees,
        search_query,
        has_results,
        expected_text,
        mock_committee,
    ):
        mock_get_committees.return_value = {"hits": [mock_committee] if has_results else []}
        mock_active_count.return_value = 42

        blocks = committees_blocks(search_query=search_query)

        assert len(blocks) > 0
        assert any(expected_text in str(block) for block in blocks)

        if has_results:
            assert any(mock_committee["idx_name"] in str(block) for block in blocks)
            assert any(mock_committee["idx_summary"] in str(block) for block in blocks)

    @patch("apps.owasp.api.search.committee.get_committees")
    @patch("apps.owasp.models.committee.Committee.active_committees_count")
    def test_committees_blocks_presentation(
        self, mock_active_count, mock_get_committees, mock_committee
    ):
        mock_get_committees.return_value = {"hits": [mock_committee]}
        mock_active_count.return_value = 42

        presentation = EntityPresentation(
            name_truncation=10,
            summary_truncation=20,
            include_feedback=False,
            include_timestamps=False,
            include_metadata=False,
        )

        blocks = committees_blocks(presentation=presentation)

        truncated_name = Truncator(mock_committee["idx_name"]).chars(10, truncate="...")
        truncated_summary = Truncator(mock_committee["idx_summary"]).chars(20, truncate="...")

        assert any(truncated_name in str(block) for block in blocks)
        assert any(truncated_summary in str(block) for block in blocks)
        assert not any(FEEDBACK_CHANNEL_MESSAGE in str(block) for block in blocks)
