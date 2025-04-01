from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.github.index.release import ReleaseIndex


class TestReleaseIndex(SimpleTestCase):
    """Test the ReleaseIndex class."""

    databases = []

    def setUp(self):
        self.model = MagicMock()
        self.client = MagicMock()
        self.settings = MagicMock()
        self.release_index = ReleaseIndex(self.model, self.client, self.settings)

    @patch("apps.common.index.IndexBase.reindex_synonyms")
    def test_update_synonyms(self, mock_reindex_synonyms):
        with patch.object(ReleaseIndex, "get_client", return_value=self.client):
            ReleaseIndex.update_synonyms()
            mock_reindex_synonyms.assert_called_once_with("github", "releases")

    def test_get_entities(self):
        mock_filter = MagicMock()

        with patch("apps.github.models.release.Release.objects") as mock_objects:
            mock_objects.filter.return_value = mock_filter

            result = self.release_index.get_entities()

            mock_objects.filter.assert_called_once_with(
                is_draft=False,
                published_at__isnull=False,
            )
            assert result == mock_filter
