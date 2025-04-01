from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.github.index.repository import RepositoryIndex


class TestRepositoryIndex(SimpleTestCase):
    """Test the RepositoryIndex class."""

    databases = []

    def setUp(self):
        self.model = MagicMock()
        self.client = MagicMock()
        self.settings = MagicMock()
        self.repository_index = RepositoryIndex(self.model, self.client, self.settings)

    @patch("apps.common.index.IndexBase.reindex_synonyms")
    def test_update_synonyms(self, mock_reindex_synonyms):
        with patch.object(RepositoryIndex, "get_client", return_value=self.client):
            RepositoryIndex.update_synonyms()
            mock_reindex_synonyms.assert_called_once_with("github", "repositories")

    def test_get_entities(self):
        mock_filter = MagicMock()
        mock_prefetch = MagicMock()

        with patch("apps.github.models.repository.Repository.objects") as mock_objects:
            mock_objects.filter.return_value = mock_filter
            mock_filter.prefetch_related.return_value = mock_prefetch

            result = self.repository_index.get_entities()

            mock_objects.filter.assert_called_once_with(is_template=False)
            mock_filter.prefetch_related.assert_called_once_with("repositorycontributor_set")
            assert result == mock_prefetch
