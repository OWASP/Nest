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
