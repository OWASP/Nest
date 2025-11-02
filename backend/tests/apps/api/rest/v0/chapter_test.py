from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.chapter import ChapterDetail, get_chapter, list_chapters


@pytest.mark.parametrize(
    "chapter_data",
    [
        {
            "country": "America",
            "created_at": "2024-11-01T00:00:00Z",
            "key": "nagoya",
            "name": "OWASP Nagoya",
            "region": "Europe",
            "updated_at": "2024-07-02T00:00:00Z",
        },
        {
            "country": "India",
            "created_at": "2023-12-01T00:00:00Z",
            "key": "something",
            "name": "OWASP something",
            "region": "Asia",
            "updated_at": "2023-09-02T00:00:00Z",
        },
    ],
)
def test_chapter_serializer_validation(chapter_data):
    class MockChapter:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
            self.nest_key = data["key"]

    chapter = ChapterDetail.from_orm(MockChapter(chapter_data))

    assert chapter.country == chapter_data["country"]
    assert chapter.created_at == datetime.fromisoformat(chapter_data["created_at"])
    assert chapter.key == chapter_data["key"]
    assert chapter.name == chapter_data["name"]
    assert chapter.region == chapter_data["region"]
    assert chapter.updated_at == datetime.fromisoformat(chapter_data["updated_at"])


class TestListChapters:
    """Test cases for list_chapters endpoint."""

    @patch("apps.api.rest.v0.chapter.ChapterModel.active_chapters")
    def test_list_chapters_with_ordering(self, mock_active_chapters):
        """Test listing chapters with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filtered_queryset = MagicMock()
        mock_ordered_queryset = MagicMock()

        mock_active_chapters.order_by.return_value = mock_ordered_queryset
        mock_filters.filter.return_value = mock_filtered_queryset

        result = list_chapters(mock_request, filters=mock_filters, ordering="created_at")

        mock_active_chapters.order_by.assert_called_once_with("created_at")
        mock_filters.filter.assert_called_once_with(mock_ordered_queryset)
        assert result == mock_filtered_queryset

    @patch("apps.api.rest.v0.chapter.ChapterModel.active_chapters")
    def test_list_chapters_with_default_ordering(self, mock_active_chapters):
        """Test that None ordering triggers default '-created_at' ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filtered_queryset = MagicMock()
        mock_ordered_queryset = MagicMock()

        mock_active_chapters.order_by.return_value = mock_ordered_queryset
        mock_filters.filter.return_value = mock_filtered_queryset

        result = list_chapters(mock_request, filters=mock_filters, ordering=None)

        mock_active_chapters.order_by.assert_called_once_with("-created_at")
        mock_filters.filter.assert_called_once_with(mock_ordered_queryset)
        assert result == mock_filtered_queryset


class TestGetChapter:
    """Test cases for get_chapter endpoint."""

    @patch("apps.api.rest.v0.chapter.ChapterModel.active_chapters")
    def test_get_chapter_with_prefix(self, mock_active_chapters):
        """Test getting a chapter when chapter_id already has www-chapter- prefix."""
        mock_request = MagicMock()
        mock_chapter = MagicMock()
        mock_filter = MagicMock()

        mock_active_chapters.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_chapter

        result = get_chapter(mock_request, chapter_id="www-chapter-london")

        mock_active_chapters.filter.assert_called_once_with(key__iexact="www-chapter-london")
        mock_filter.first.assert_called_once()
        assert result == mock_chapter

    @patch("apps.api.rest.v0.chapter.ChapterModel.active_chapters")
    def test_get_chapter_without_prefix(self, mock_active_chapters):
        """Test getting a chapter when chapter_id needs www-chapter- prefix added."""
        mock_request = MagicMock()
        mock_chapter = MagicMock()
        mock_filter = MagicMock()

        mock_active_chapters.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_chapter

        result = get_chapter(mock_request, chapter_id="london")

        mock_active_chapters.filter.assert_called_once_with(key__iexact="www-chapter-london")
        mock_filter.first.assert_called_once()
        assert result == mock_chapter

    @patch("apps.api.rest.v0.chapter.ChapterModel.active_chapters")
    def test_get_chapter_not_found(self, mock_active_chapters):
        """Test getting a chapter that does not exist returns 404."""
        mock_request = MagicMock()
        mock_filter = MagicMock()

        mock_active_chapters.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        result = get_chapter(mock_request, chapter_id="nonexistent")

        mock_active_chapters.filter.assert_called_once_with(key__iexact="www-chapter-nonexistent")
        mock_filter.first.assert_called_once()
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert b"Chapter not found" in result.content

    @patch("apps.api.rest.v0.chapter.ChapterModel.active_chapters")
    def test_get_chapter_uppercase_prefix(self, mock_active_chapters):
        """Test that uppercase prefix is detected case-insensitively."""
        mock_request = MagicMock()
        mock_filter = MagicMock()
        mock_chapter = MagicMock()

        mock_active_chapters.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_chapter

        result = get_chapter(mock_request, chapter_id="WWW-CHAPTER-London")

        # Prefix should be detected case-insensitively, no double prefix
        mock_active_chapters.filter.assert_called_once_with(key__iexact="WWW-CHAPTER-London")
        mock_filter.first.assert_called_once()
        assert result == mock_chapter
