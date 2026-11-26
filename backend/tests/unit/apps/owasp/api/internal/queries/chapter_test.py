from unittest.mock import MagicMock, Mock, patch

import pytest

from apps.common.constants import MAX_SEARCH_QUERY_LENGTH
from apps.owasp.api.internal.queries.chapter import SEARCH_CHAPTERS_LIMIT, ChapterQuery
from apps.owasp.models.chapter import Chapter

GITHUB_USER_FILTER_PATH = "apps.owasp.api.internal.queries.chapter.GithubUser.objects.filter"


class TestChapterQuery:
    """Test cases for ChapterQuery class."""

    def test_has_strawberry_definition(self):
        """Test if ChapterQuery is a valid Strawberry type and has expected fields."""
        assert hasattr(ChapterQuery, "__strawberry_definition__")

        field_names = [field.name for field in ChapterQuery.__strawberry_definition__.fields]
        assert "chapter" in field_names
        assert "chapter_countries" in field_names
        assert "is_chapter_leader" in field_names
        assert "recent_chapters" in field_names
        assert "search_chapters" in field_names


class TestChapterResolution:
    """Test cases for chapter resolution methods."""

    @pytest.fixture
    def mock_info(self):
        """Mock GraphQL ResolveInfo object."""
        return Mock()

    @pytest.fixture
    def mock_chapter(self):
        """Mock Chapter instance."""
        return Mock(spec=Chapter)

    def test_chapter_found(self, mock_info, mock_chapter):
        """Test if a chapter is returned when found."""
        with patch("apps.owasp.models.chapter.Chapter.get_by_key") as mock_get:
            mock_get.return_value = mock_chapter

            result = ChapterQuery().chapter(key="test-chapter")

            assert result == mock_chapter
            mock_get.assert_called_once_with("test-chapter", active_only=False)

    def test_chapter_not_found(self, mock_info):
        """Test if None is returned when the chapter is not found."""
        with patch("apps.owasp.models.chapter.Chapter.get_by_key", return_value=None):
            result = ChapterQuery().chapter(key="non-existent")

            assert result is None

    def test_recent_chapters_query(self, mock_info):
        """Test if recent chapters are returned correctly."""
        mock_chapters = [Mock(), Mock()]

        # Mock the method directly on the instance
        query = ChapterQuery()
        with patch.object(query, "recent_chapters", return_value=mock_chapters):
            result = query.recent_chapters(limit=2)
            assert result == mock_chapters

    def test_recent_chapters_with_invalid_limit(self, mock_info):
        """Test recent_chapters with invalid limit returns empty list."""
        query = ChapterQuery()
        result = query.recent_chapters(limit=0)
        assert result == []
        result = query.recent_chapters(limit=-1)
        assert result == []

    def test_recent_chapters_with_valid_limit(self, mock_info):
        """Test recent_chapters with valid limit returns chapters."""
        mock_chapters = [Mock(), Mock()]
        query = ChapterQuery()
        with patch.object(Chapter, "active_chapters") as mock_active:
            mock_qs = Mock()
            mock_active.order_by.return_value = mock_qs
            mock_qs.__getitem__ = Mock(return_value=mock_chapters)

            result = query.recent_chapters(limit=5)

            mock_active.order_by.assert_called_once_with("-created_at")
            mock_qs.__getitem__.assert_called_once_with(slice(None, 5, None))
            assert result == mock_chapters

    def test_chapter_countries_returns_sorted_distinct_countries(self, mock_info):
        """Test chapter_countries returns sorted distinct country names."""
        query = ChapterQuery()
        with patch.object(Chapter, "active_chapters") as mock_active:
            mock_qs = Mock()
            mock_active.exclude.return_value = mock_qs
            mock_values_qs = Mock()
            mock_qs.values_list.return_value = mock_values_qs
            mock_values_qs.distinct.return_value = ["Japan", "Germany", "United States"]

            result = query.chapter_countries()

            mock_active.exclude.assert_called_once_with(country="")
            mock_qs.values_list.assert_called_once_with("country", flat=True)
            mock_values_qs.distinct.assert_called_once()
            assert result == ["Germany", "Japan", "United States"]

    def test_chapter_countries_returns_empty_list_when_no_chapters(self, mock_info):
        """Test chapter_countries returns empty list when no active chapters."""
        query = ChapterQuery()
        with patch.object(Chapter, "active_chapters") as mock_active:
            mock_qs = Mock()
            mock_active.exclude.return_value = mock_qs
            mock_values_qs = Mock()
            mock_qs.values_list.return_value = mock_values_qs
            mock_values_qs.distinct.return_value = []

            result = query.chapter_countries()

            assert result == []


class TestSearchChapters:
    """Test cases for search_chapters query."""

    def test_search_chapters_short_query(self):
        """Test search_chapters returns empty for short queries."""
        query = ChapterQuery()
        result = query.search_chapters(query="ab")
        assert result == []

    def test_search_chapters_long_query(self):
        """Test search_chapters returns empty for queries exceeding max length."""
        query = ChapterQuery()
        result = query.search_chapters(query="a" * 101)
        assert result == []

    def test_search_chapters_valid_query(self):
        """Test search_chapters returns matching chapters."""
        mock_chapters = [Mock(), Mock()]
        query = ChapterQuery()
        with patch.object(Chapter, "active_chapters") as mock_active:
            mock_qs = Mock()
            mock_active.filter.return_value = mock_qs
            mock_ordered_qs = Mock()
            mock_qs.order_by.return_value = mock_ordered_qs
            mock_ordered_qs.__getitem__ = Mock(return_value=mock_chapters)

            result = query.search_chapters(query="test")

            mock_active.filter.assert_called_once_with(name__icontains="test")
            mock_qs.order_by.assert_called_once_with("name")
            mock_ordered_qs.__getitem__.assert_called_once_with(slice(None, SEARCH_CHAPTERS_LIMIT))
            assert result == mock_chapters

    def test_search_chapters_whitespace_query(self):
        """Test search_chapters strips whitespace before checking length."""
        query = ChapterQuery()
        result = query.search_chapters(query="  ab  ")
        assert result == []


class TestSearchChaptersResolution:
    """Test cases for resolving search_chapters field."""

    @pytest.mark.parametrize(
        "query",
        [
            "ab",
            "  ab  ",
            "a" * (MAX_SEARCH_QUERY_LENGTH + 1),
        ],
    )
    def test_search_chapters_invalid_query_length_returns_empty(self, query):
        """Test search_chapters returns [] for too-short or too-long queries."""
        with patch.object(Chapter, "active_chapters") as mock_active:
            result = ChapterQuery().search_chapters(query=query)

        assert result == []
        mock_active.filter.assert_not_called()

    def test_search_chapters_filters_active_chapters_by_name(self):
        """Test search_chapters filters active chapters by trimmed name and limits results."""
        mock_chapters = [Mock(spec=Chapter)]

        with patch.object(Chapter, "active_chapters") as mock_active:
            mock_ordered = MagicMock()
            mock_ordered.__getitem__.return_value = mock_chapters
            mock_active.filter.return_value.order_by.return_value = mock_ordered

            result = ChapterQuery().search_chapters(query="  london  ")

        assert result == mock_chapters
        mock_active.filter.assert_called_once_with(name__icontains="london")
        mock_active.filter.return_value.order_by.assert_called_once_with("name")
        mock_ordered.__getitem__.assert_called_once_with(slice(None, SEARCH_CHAPTERS_LIMIT, None))


class TestIsChapterLeaderResolution:
    """Test cases for resolving is_chapter_leader field."""

    def test_is_chapter_leader_user_not_found(self):
        """Test is_chapter_leader returns False when the user doesn't exist."""
        with patch(GITHUB_USER_FILTER_PATH) as mock_filter:
            mock_filter.return_value.first.return_value = None

            result = ChapterQuery().is_chapter_leader(login="nonexistent")

        assert result is False
        mock_filter.assert_called_once_with(login__iexact="nonexistent")

    def test_is_chapter_leader_user_is_leader(self):
        """Test is_chapter_leader returns True when the user leads a chapter."""
        mock_user = Mock()
        mock_user.chapters.exists.return_value = True

        with patch(GITHUB_USER_FILTER_PATH) as mock_filter:
            mock_filter.return_value.first.return_value = mock_user

            result = ChapterQuery().is_chapter_leader(login="leader")

        assert result is True
        mock_user.chapters.exists.assert_called_once_with()

    def test_is_chapter_leader_user_not_leader(self):
        """Test is_chapter_leader returns False when the user leads no chapter."""
        mock_user = Mock()
        mock_user.chapters.exists.return_value = False

        with patch(GITHUB_USER_FILTER_PATH) as mock_filter:
            mock_filter.return_value.first.return_value = mock_user

            result = ChapterQuery().is_chapter_leader(login="member")

        assert result is False

    def test_is_chapter_leader_strips_login(self):
        """Test is_chapter_leader trims the login before a case-insensitive lookup."""
        with patch(GITHUB_USER_FILTER_PATH) as mock_filter:
            mock_filter.return_value.first.return_value = None

            ChapterQuery().is_chapter_leader(login="  Leader  ")

        mock_filter.assert_called_once_with(login__iexact="Leader")
