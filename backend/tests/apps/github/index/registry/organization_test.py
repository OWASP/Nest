from unittest.mock import MagicMock, patch

import pytest

from apps.github.index.registry.organization import OrganizationIndex
from apps.github.models.organization import Organization


@pytest.fixture
def organization_index(mocker):
    """Return an instance of the OrganizationIndex."""
    mocker.patch("apps.common.index.IndexBase.__init__", return_value=None)
    return OrganizationIndex()


class TestOrganizationIndex:
    def test_class_attributes(self):
        """Test that the basic class attributes are set correctly."""
        assert OrganizationIndex.index_name == "organizations"
        assert OrganizationIndex.should_index == "is_indexable"
        assert isinstance(OrganizationIndex.fields, tuple)
        assert len(OrganizationIndex.fields) > 0
        assert isinstance(OrganizationIndex.settings, dict)
        assert "minProximity" in OrganizationIndex.settings

    @patch("apps.github.index.registry.organization.OrganizationIndex.reindex_synonyms")
    def test_update_synonyms(self, mock_reindex_synonyms):
        """Test that update_synonyms calls the parent method with correct args."""
        OrganizationIndex.update_synonyms()
        mock_reindex_synonyms.assert_called_once_with("github", "organizations")

    def test_get_entities(self, organization_index):
        """Test that get_entities constructs the correct queryset by calling.

        Organization.objects.filter with the expected argument.
        """
        mock_filter_manager = MagicMock()
        mock_filter_manager.filter.return_value = "final_queryset"

        with patch.object(Organization, "objects", mock_filter_manager):
            queryset = organization_index.get_entities()

            mock_filter_manager.filter.assert_called_once_with(is_owasp_related_organization=True)
            assert queryset == "final_queryset"
