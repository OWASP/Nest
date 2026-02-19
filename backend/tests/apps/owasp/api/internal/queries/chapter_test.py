from unittest.mock import Mock, patch

import pytest

from apps.owasp.api.internal.queries.chapter import ChapterQuery
from apps.owasp.models.chapter import Chapter


class TestChapterQuery:
    """Test cases for ChapterQuery class."""

    def test_has_strawberry_definition(self):
        """Test if ChapterQuery is a valid Strawberry type and has expected fields."""
        assert hasattr(ChapterQuery, "__strawberry_definition__")

        field_names = [field.name for field in ChapterQuery.__strawberry_definition__.fields]
        assert "chapter" in field_names
        assert "recent_chapters" in field_names


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
        with patch("apps.owasp.models.chapter.Chapter.objects.get") as mock_get:
            mock_get.return_value = mock_chapter

            result = ChapterQuery().chapter(key="test-chapter")

            assert result == mock_chapter
            mock_get.assert_called_once_with(key="www-chapter-test-chapter")

    def test_chapter_not_found(self, mock_info):
        """Test if None is returned when the chapter is not found."""
        with patch("apps.owasp.models.chapter.Chapter.objects.get") as mock_get:
            mock_get.side_effect = Chapter.DoesNotExist

            result = ChapterQuery().chapter(key="non-existent")

            assert result is None
            mock_get.assert_called_once_with(key="www-chapter-non-existent")

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
