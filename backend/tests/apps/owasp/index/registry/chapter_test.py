from unittest.mock import patch

from apps.owasp.index.registry.chapter import ChapterIndex


class TestChapterIndex:
    def test_get_entities(self):
        """Test get_entities returns active chapters with select_related."""
        with patch.object(ChapterIndex, "__init__", lambda _: None):
            index = ChapterIndex()

        with patch("apps.owasp.index.registry.chapter.Chapter") as mock_chapter:
            mock_manager = mock_chapter.active_chapters
            mock_manager.select_related.return_value = ["chapter1", "chapter2"]

            result = index.get_entities()

            mock_manager.select_related.assert_called_once_with("owasp_repository")
            assert result == ["chapter1", "chapter2"]
