from unittest.mock import MagicMock, patch

import pytest

from apps.github.index.registry.release import ReleaseIndex
from apps.github.models.release import Release


@pytest.fixture
def release_index(mocker):
    """Return an instance of the ReleaseIndex."""
    mocker.patch("apps.common.index.IndexBase.__init__", return_value=None)
    return ReleaseIndex()


class TestReleaseIndex:
    def test_class_attributes(self):
        """Test that the basic class attributes are set correctly."""
        assert ReleaseIndex.index_name == "releases"
        assert ReleaseIndex.should_index == "is_indexable"
        assert isinstance(ReleaseIndex.fields, tuple)
        assert len(ReleaseIndex.fields) > 0
        assert isinstance(ReleaseIndex.settings, dict)
        assert "minProximity" in ReleaseIndex.settings

    @patch("apps.github.index.registry.release.ReleaseIndex.reindex_synonyms")
    def test_update_synonyms(self, mock_reindex_synonyms):
        """Test that update_synonyms calls the parent method with correct args."""
        ReleaseIndex.update_synonyms()
        mock_reindex_synonyms.assert_called_once_with("github", "releases")

    def test_get_entities(self, release_index):
        """Test that get_entities constructs the correct queryset by calling.

        Release.objects.filter with the expected arguments.
        """
        mock_filter_manager = MagicMock()
        mock_filter_manager.filter.return_value = "final_queryset"

        with patch.object(Release, "objects", mock_filter_manager):
            queryset = release_index.get_entities()

            mock_filter_manager.filter.assert_called_once_with(
                is_draft=False,
                published_at__isnull=False,
            )
            assert queryset == "final_queryset"
