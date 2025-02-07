from unittest.mock import Mock, patch

import pytest
from graphene import Field, NonNull, String

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.chapter import ChapterNode
from apps.owasp.graphql.queries.chapter import ChapterQuery
from apps.owasp.models.chapter import Chapter


class TestChapterQuery:
    """Test cases for ChapterQuery class."""

    def test_chapter_query_inheritance(self):
        """Test if ChapterQuery inherits from BaseQuery."""
        assert issubclass(ChapterQuery, BaseQuery)

    def test_chapter_field_configuration(self):
        """Test if chapter field is properly configured."""
        chapter_field = ChapterQuery._meta.fields.get("chapter")
        assert isinstance(chapter_field, Field)
        assert chapter_field.type == ChapterNode

        assert "key" in chapter_field.args
        key_arg = chapter_field.args["key"]
        assert isinstance(key_arg.type, NonNull)
        assert key_arg.type.of_type == String

    class TestChapterResolution:
        """Test cases for chapter resolution."""

        @pytest.fixture()
        def mock_chapter(self):
            """Chapter mock fixture."""
            return Mock(spec=Chapter)

        @pytest.fixture()
        def mock_info(self):
            """GraphQL info mock fixture."""
            return Mock()

        def test_resolve_chapter_existing(self, mock_chapter, mock_info):
            """Test resolving an existing chapter."""
            with patch("apps.owasp.models.chapter.Chapter.objects.get") as mock_get:
                mock_get.return_value = mock_chapter

                result = ChapterQuery.resolve_chapter(None, mock_info, key="test-chapter")

                assert result == mock_chapter
                mock_get.assert_called_once_with(key="www-chapter-test-chapter")

        def test_resolve_chapter_not_found(self, mock_info):
            """Test resolving a non-existent chapter."""
            with patch("apps.owasp.models.chapter.Chapter.objects.get") as mock_get:
                mock_get.side_effect = Chapter.DoesNotExist

                result = ChapterQuery.resolve_chapter(None, mock_info, key="non-existent")

                assert result is None
                mock_get.assert_called_once_with(key="www-chapter-non-existent")
