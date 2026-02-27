from unittest.mock import patch

from apps.owasp.index.registry.chapter import ChapterIndex


class TestChapterIndex:
    @patch("apps.common.index.IndexBase.configure_replicas")
    def test_configure_replicas(self, mock_configure_replicas):
        """Test that configure_replicas calls the parent method with correct args."""
        ChapterIndex.configure_replicas()
        assert mock_configure_replicas.call_count == 1
        assert mock_configure_replicas.call_args[0][0] == "chapters"
        assert isinstance(mock_configure_replicas.call_args[0][1], dict)

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
