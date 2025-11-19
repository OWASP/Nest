from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.organization import (
    OrganizationDetail,
    get_organization,
    list_organization,
)


class TestOrganizationSchema:
    @pytest.mark.parametrize(
        "organization_data",
        [
            {
                "company": "GitHub, Inc.",
                "created_at": "2024-12-30T00:00:00Z",
                "location": "San Francisco, CA",
                "login": "github",
                "name": "GitHub",
                "updated_at": "2024-12-30T00:00:00Z",
            },
            {
                "company": "Microsoft Corporation",
                "created_at": "2024-12-29T00:00:00Z",
                "location": "Redmond, WA",
                "login": "microsoft",
                "name": "Microsoft",
                "updated_at": "2024-12-30T00:00:00Z",
            },
        ],
    )
    def test_organization_schema(self, organization_data):
        organization = OrganizationDetail(**organization_data)

        assert organization.company == organization_data["company"]
        assert organization.created_at == datetime.fromisoformat(organization_data["created_at"])
        assert organization.location == organization_data["location"]
        assert organization.login == organization_data["login"]
        assert organization.name == organization_data["name"]
        assert organization.updated_at == datetime.fromisoformat(organization_data["updated_at"])


class TestListOrganization:
    """Test cases for list_organization endpoint."""

    @patch("apps.api.rest.v0.organization.OrganizationModel.objects")
    def test_list_organization_with_custom_ordering(self, mock_objects):
        """Test listing organizations with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_base_filter = MagicMock()
        mock_ordered = MagicMock()
        mock_final = MagicMock()

        mock_objects.filter.return_value = mock_base_filter
        mock_base_filter.order_by.return_value = mock_ordered
        mock_filters.filter.return_value = mock_final

        result = list_organization(mock_request, filters=mock_filters, ordering="created_at")

        mock_objects.filter.assert_called_once_with(is_owasp_related_organization=True)
        mock_base_filter.order_by.assert_called_once_with("created_at")
        mock_filters.filter.assert_called_once_with(mock_ordered)
        assert result == mock_final

    @patch("apps.api.rest.v0.organization.OrganizationModel.objects")
    def test_list_organization_with_default_ordering(self, mock_objects):
        """Test listing organizations with default ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_base_filter = MagicMock()
        mock_ordered = MagicMock()
        mock_final = MagicMock()

        mock_objects.filter.return_value = mock_base_filter
        mock_base_filter.order_by.return_value = mock_ordered
        mock_filters.filter.return_value = mock_final

        result = list_organization(mock_request, filters=mock_filters, ordering=None)

        mock_objects.filter.assert_called_once_with(is_owasp_related_organization=True)
        mock_base_filter.order_by.assert_called_once_with("-created_at")
        mock_filters.filter.assert_called_once_with(mock_ordered)
        assert result == mock_final


class TestGetOrganization:
    """Test cases for get_organization endpoint."""

    @patch("apps.api.rest.v0.organization.OrganizationModel.objects")
    def test_get_organization_found(self, mock_objects):
        """Test getting an organization that exists."""
        mock_request = MagicMock()
        mock_filter = MagicMock()
        mock_org = MagicMock()

        mock_objects.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_org

        result = get_organization(mock_request, organization_id="OWASP")

        mock_objects.filter.assert_called_once_with(
            is_owasp_related_organization=True,
            login__iexact="OWASP",
        )
        mock_filter.first.assert_called_once()
        assert result == mock_org

    @patch("apps.api.rest.v0.organization.OrganizationModel.objects")
    def test_get_organization_not_found(self, mock_objects):
        """Test getting an organization that does not exist returns 404."""
        mock_request = MagicMock()
        mock_filter = MagicMock()

        mock_objects.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        result = get_organization(mock_request, organization_id="NonExistent")

        mock_objects.filter.assert_called_once_with(
            is_owasp_related_organization=True,
            login__iexact="NonExistent",
        )
        mock_filter.first.assert_called_once()
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert b"Organization not found" in result.content
