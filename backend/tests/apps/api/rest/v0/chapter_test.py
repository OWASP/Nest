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
            "latitude": 35.1815,
            "longitude": 136.9066,
            "name": "OWASP Nagoya",
            "region": "Europe",
            "updated_at": "2024-07-02T00:00:00Z",
        },
        {
            "country": "India",
            "created_at": "2023-12-01T00:00:00Z",
            "key": "something",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "name": "OWASP something",
            "region": "Asia",
            "updated_at": "2023-09-02T00:00:00Z",
        },
    ],
)
def test_chapter_serializer_validation(chapter_data):
    class MockMember:
        def __init__(self, login):
            self.login = login

    class MockEntityMember:
        def __init__(self, name, login=None):
            self.member = MockMember(login) if login else None
            self.member_name = name

    class MockChapter:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
            self.nest_key = data["key"]
            self.entity_leaders = [
                MockEntityMember("Alice", "alice"),
                MockEntityMember("Bob"),
            ]

    chapter = ChapterDetail.from_orm(MockChapter(chapter_data))

    assert chapter.country == chapter_data["country"]
    assert chapter.created_at == datetime.fromisoformat(chapter_data["created_at"])
    assert chapter.key == chapter_data["key"]
    assert chapter.latitude == chapter_data["latitude"]
    assert chapter.longitude == chapter_data["longitude"]
    assert len(chapter.leaders) == 2
    assert chapter.leaders[0].key == "alice"
    assert chapter.leaders[0].name == "Alice"
    assert chapter.leaders[1].key is None
    assert chapter.leaders[1].name == "Bob"
    assert chapter.name == chapter_data["name"]
    assert chapter.region == chapter_data["region"]
    assert chapter.updated_at == datetime.fromisoformat(chapter_data["updated_at"])


class TestListChapters:
    """Tests for list_chapters endpoint."""

    @patch("apps.api.rest.v0.chapter.ChapterModel")
    def test_list_chapters_no_filter(self, mock_chapter_model):
        """Test listing chapters without filters."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_chapter_model.active_chapters.order_by.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_chapters(mock_request, mock_filters, ordering=None)

        mock_chapter_model.active_chapters.order_by.assert_called_with("-created_at")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.chapter.ChapterModel")
    def test_list_chapters_with_ordering(self, mock_chapter_model):
        """Test listing chapters with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_chapter_model.active_chapters.order_by.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_chapters(mock_request, mock_filters, ordering="latitude")

        mock_chapter_model.active_chapters.order_by.assert_called_with("latitude")
        assert result == mock_queryset


class TestGetChapter:
    """Tests for get_chapter endpoint."""

    @patch("apps.api.rest.v0.chapter.ChapterModel")
    def test_get_chapter_success(self, mock_chapter_model):
        """Test getting a chapter when found."""
        mock_request = MagicMock()
        mock_chapter = MagicMock()
        mock_chapter_model.active_chapters.filter.return_value.first.return_value = mock_chapter

        result = get_chapter(mock_request, "London")

        mock_chapter_model.active_chapters.filter.assert_called_with(
            key__iexact="www-chapter-London"
        )
        assert result == mock_chapter

    @patch("apps.api.rest.v0.chapter.ChapterModel")
    def test_get_chapter_with_prefix(self, mock_chapter_model):
        """Test getting a chapter with www-chapter- prefix."""
        mock_request = MagicMock()
        mock_chapter = MagicMock()
        mock_chapter_model.active_chapters.filter.return_value.first.return_value = mock_chapter

        result = get_chapter(mock_request, "www-chapter-London")

        mock_chapter_model.active_chapters.filter.assert_called_with(
            key__iexact="www-chapter-London"
        )
        assert result == mock_chapter

    @patch("apps.api.rest.v0.chapter.ChapterModel")
    def test_get_chapter_not_found(self, mock_chapter_model):
        """Test getting a chapter when not found."""
        mock_request = MagicMock()
        mock_chapter_model.active_chapters.filter.return_value.first.return_value = None

        result = get_chapter(mock_request, "NonExistent")

        assert result.status_code == HTTPStatus.NOT_FOUND
