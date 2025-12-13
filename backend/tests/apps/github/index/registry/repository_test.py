from unittest.mock import MagicMock, patch

import pytest

from apps.github.index.registry.repository import RepositoryIndex
from apps.github.models.repository import Repository


@pytest.fixture
def repository_index(mocker):
    """Return an instance of the RepositoryIndex."""
    mocker.patch("apps.common.index.IndexBase.__init__", return_value=None)
    return RepositoryIndex()


class TestRepositoryIndex:
    def test_class_attributes(self):
        """Test that the basic class attributes are set correctly."""
        assert RepositoryIndex.index_name == "repositories"
        assert RepositoryIndex.should_index == "is_indexable"
        assert isinstance(RepositoryIndex.fields, tuple)
        assert len(RepositoryIndex.fields) > 0
        assert isinstance(RepositoryIndex.settings, dict)
        assert "minProximity" in RepositoryIndex.settings

    @patch("apps.github.index.registry.repository.RepositoryIndex.reindex_synonyms")
    def test_update_synonyms(self, mock_reindex_synonyms):
        """Test that update_synonyms calls the parent method with correct args."""
        RepositoryIndex.update_synonyms()
        mock_reindex_synonyms.assert_called_once_with("github", "repositories")

    def test_get_entities(self, repository_index):
        """Test that get_entities constructs the correct queryset by chaining.

        the expected manager methods.
        """
        mock_manager = MagicMock()
        mock_manager.filter.return_value.prefetch_related.return_value = "final_queryset"

        with patch.object(Repository, "objects", mock_manager):
            queryset = repository_index.get_entities()

            mock_manager.filter.assert_called_once_with(is_template=False)
            mock_manager.filter.return_value.prefetch_related.assert_called_once_with(
                "repositorycontributor_set"
            )
            assert queryset == "final_queryset"
