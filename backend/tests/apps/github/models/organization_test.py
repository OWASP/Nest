from unittest.mock import Mock, patch

from apps.github.models.organization import Organization


class TestOrganizationModel:
    def test_str_representation(self):
        organization = Organization(name="Organization Name")
        assert str(organization) == "Organization Name"

    def test_bulk_save(self):
        mock_org = [Mock(id=None), Mock(id=1)]
        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            Organization.bulk_save(mock_org)
            mock_bulk_save.assert_called_once_with(Organization, mock_org, fields=None)

    @patch("apps.github.models.organization.Organization.objects.get")
    def test_update_data(self, mock_get):
        mock_get.side_effect = Organization.DoesNotExist

        gh_organization_mock = Mock()
        gh_organization_mock.raw_data = {"node_id": "12345"}

        with (
            patch.object(Organization, "save", return_value=None) as mock_save,
            patch.object(Organization, "from_github") as mock_from_github,
        ):
            Organization.update_data(gh_organization_mock)

            mock_save.assert_called_once()
            mock_from_github.assert_called_once_with(gh_organization_mock)

    def test_from_github(self):
        gh_organization_mock = Mock()
        gh_organization_mock.description = "Description"

        organization = Organization()
        organization.from_github(gh_organization_mock)

        assert organization.description == gh_organization_mock.description

    def test_related_projects_property(self):
        """Test the related_projects property."""
        with (
            patch("apps.github.models.organization.apps.get_model") as mock_get_model,
        ):
            mock_project = Mock()
            mock_queryset = Mock()
            mock_queryset.select_related.return_value.prefetch_related.return_value.filter.return_value.distinct.return_value = [mock_project]
            mock_get_model.return_value.objects = mock_queryset

            organization = Organization()
            
            # Mock the repositories.all() return value
            mock_repo_manager = Mock()
            mock_repo_manager.all.return_value = [Mock()]
            
            with patch.object(Organization, 'repositories', mock_repo_manager, create=True):
                projects = organization.related_projects
                assert list(projects) == [mock_project]

    @patch("apps.github.models.organization.Organization.objects.values_list")
    def test_get_logins(self, mock_values_list):
        """Test get_logins static method."""
        mock_values_list.return_value = ["org1", "org2", "org3"]
        logins = Organization.get_logins()
        assert logins == {"org1", "org2", "org3"}
        mock_values_list.assert_called_once_with("login", flat=True)

    @patch("apps.github.models.organization.Organization.objects.get")
    def test_update_data_without_save(self, mock_get):
        """Test update_data with save=False."""
        mock_org = Mock(spec=Organization)
        mock_get.return_value = mock_org

        gh_organization_mock = Mock()
        gh_organization_mock.raw_data = {"node_id": "org_node_123"}

        org = Organization.update_data(gh_organization_mock, save=False)

        mock_org.from_github.assert_called_once_with(gh_organization_mock)
        mock_org.save.assert_not_called()
        assert org == mock_org

    def test_from_github_with_none_value(self):
        """Test from_github when a field value is None."""
        gh_organization_mock = Mock()
        gh_organization_mock.description = None

        organization = Organization()
        original_description = organization.description
        organization.from_github(gh_organization_mock)
    
        # None values shouldn't update the field
        assert organization.description == original_description

    @patch("apps.github.models.organization.Organization.objects.values_list")
    def test_get_logins(self, mock_values_list):
        """Test get_logins static method."""
        mock_values_list.return_value = ["org1", "org2", "org3"]
        
        # Clear the cache before testing
        Organization.get_logins.cache_clear()
        
        logins = Organization.get_logins()
        assert logins == {"org1", "org2", "org3"}
        mock_values_list.assert_called_once_with("login", flat=True)
