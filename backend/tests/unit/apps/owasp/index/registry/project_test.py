from unittest.mock import MagicMock, patch

import pytest

from apps.owasp.index.registry.project import ProjectIndex
from apps.owasp.models.project import Project


@pytest.fixture
def project_index(mocker):
    """Return an instance of the ProjectIndex."""
    mocker.patch("apps.common.index.IndexBase.__init__", return_value=None)
    return ProjectIndex()


class TestProjectIndex:
    def test_class_attributes(self):
        """Test that the basic class attributes are set correctly."""
        assert ProjectIndex.index_name == "projects"
        assert ProjectIndex.should_index == "is_indexable"
        assert isinstance(ProjectIndex.fields, tuple)
        assert len(ProjectIndex.fields) > 0
        assert isinstance(ProjectIndex.settings, dict)
        assert "attributesForFaceting" in ProjectIndex.settings

    @patch("apps.common.index.IndexBase.configure_replicas")
    def test_configure_replicas(self, mock_configure_replicas):
        """Test that configure_replicas calls the parent method with correct args."""
        ProjectIndex.configure_replicas()
        assert mock_configure_replicas.call_count == 1
        assert mock_configure_replicas.call_args[0][0] == "projects"
        assert isinstance(mock_configure_replicas.call_args[0][1], dict)

    @patch("apps.common.index.IndexBase.reindex_synonyms")
    def test_update_synonyms(self, mock_reindex_synonyms):
        """Test that update_synonyms calls the parent method with correct args."""
        ProjectIndex.update_synonyms()
        mock_reindex_synonyms.assert_called_once_with("owasp", "projects")

    def test_get_entities(self, project_index):
        """Test that get_entities constructs the correct queryset by chaining."""
        mock_manager = MagicMock()
        mock_manager.prefetch_related.return_value.filter.return_value.distinct.return_value = (
            "final_queryset"
        )

        with patch.object(Project, "objects", mock_manager):
            queryset = project_index.get_entities()

            mock_manager.prefetch_related.assert_called_once_with(
                "organizations",
                "repositories",
            )
            mock_manager.prefetch_related.return_value.filter.assert_called_once_with(
                organizations__isnull=False
            )
            mock_manager.prefetch_related.return_value.filter.return_value.distinct.assert_called_once()
            assert queryset == "final_queryset"
