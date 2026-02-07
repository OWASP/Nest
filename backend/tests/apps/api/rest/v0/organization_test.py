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
    """Tests for list_organization endpoint."""

    @patch("apps.api.rest.v0.organization.OrganizationModel")
    def test_list_organization_no_ordering(self, mock_org_model):
        """Test listing organizations without ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_org_model.objects.filter.return_value.order_by.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_organization(mock_request, mock_filters, ordering=None)

        mock_org_model.objects.filter.assert_called_with(is_owasp_related_organization=True)
        assert result == mock_queryset

    @patch("apps.api.rest.v0.organization.OrganizationModel")
    def test_list_organization_with_ordering(self, mock_org_model):
        """Test listing organizations with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_org_model.objects.filter.return_value.order_by.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_organization(mock_request, mock_filters, ordering="updated_at")

        mock_org_model.objects.filter.return_value.order_by.assert_called_with("updated_at")
        assert result == mock_queryset


class TestGetOrganization:
    """Tests for get_organization endpoint."""

    @patch("apps.api.rest.v0.organization.OrganizationModel")
    def test_get_organization_success(self, mock_org_model):
        """Test getting an organization when found."""
        mock_request = MagicMock()
        mock_org = MagicMock()
        mock_org_model.objects.filter.return_value.first.return_value = mock_org

        result = get_organization(mock_request, "OWASP")

        mock_org_model.objects.filter.assert_called_with(
            is_owasp_related_organization=True, login__iexact="OWASP"
        )
        assert result == mock_org

    @patch("apps.api.rest.v0.organization.OrganizationModel")
    def test_get_organization_not_found(self, mock_org_model):
        """Test getting an organization when not found."""
        mock_request = MagicMock()
        mock_org_model.objects.filter.return_value.first.return_value = None

        result = get_organization(mock_request, "NonExistent")

        assert result.status_code == HTTPStatus.NOT_FOUND
