"""Test cases for OrganizationQuery."""

from unittest.mock import Mock, patch

import pytest

from apps.github.api.internal.queries.organization import OrganizationQuery
from apps.github.models.organization import Organization


class TestOrganizationQuery:
    """Test cases for OrganizationQuery class."""

    @pytest.fixture
    def mock_organization(self):
        """Mock Organization instance."""
        org = Mock(spec=Organization)
        org.id = 1
        org.login = "owasp"
        return org

    @patch("apps.github.models.organization.Organization.objects.get")
    def test_organization_found(self, mock_get, mock_organization):
        """Test fetching organization when it exists."""
        mock_get.return_value = mock_organization

        result = OrganizationQuery().organization(login="owasp")

        assert result == mock_organization
        mock_get.assert_called_once_with(is_owasp_related_organization=True, login="owasp")

    @patch("apps.github.models.organization.Organization.objects.get")
    def test_organization_not_found(self, mock_get):
        """Test fetching organization when it doesn't exist."""
        mock_get.side_effect = Organization.DoesNotExist()

        result = OrganizationQuery().organization(login="nonexistent")

        assert result is None
        mock_get.assert_called_once_with(is_owasp_related_organization=True, login="nonexistent")

    @patch("apps.github.models.organization.Organization.objects.get")
    def test_organization_with_different_login(self, mock_get, mock_organization):
        """Test fetching organization with different login."""
        mock_get.return_value = mock_organization

        result = OrganizationQuery().organization(login="test-org")

        assert result == mock_organization
        mock_get.assert_called_once_with(is_owasp_related_organization=True, login="test-org")

    @patch("apps.github.models.organization.Organization.objects.filter")
    def test_recent_organizations(self, mock_filter):
        """Test fetching recent organizations."""
        mock_qs = Mock()
        mock_ordered_qs = Mock()
        mock_filter.return_value = mock_qs
        mock_qs.order_by.return_value = mock_ordered_qs
        mock_ordered_qs.__getitem__ = Mock(return_value=["org1", "org2"])

        result = OrganizationQuery().recent_organizations(limit=2)

        assert result == ["org1", "org2"]
        mock_filter.assert_called_once_with(is_owasp_related_organization=True)
        mock_qs.order_by.assert_called_once_with("-created_at")
        mock_ordered_qs.__getitem__.assert_called_once_with(slice(None, 2))

    @patch("apps.github.models.organization.Organization.objects.filter")
    def test_recent_organizations_with_zero_limit(self, mock_filter):
        """Test fetching recent organizations with zero limit returns empty list."""
        result = OrganizationQuery().recent_organizations(limit=0)

        assert result == []
        mock_filter.assert_not_called()

    @patch("apps.github.models.organization.Organization.objects.filter")
    def test_recent_organizations_with_negative_limit(self, mock_filter):
        """Test fetching recent organizations with negative limit returns empty list."""
        result = OrganizationQuery().recent_organizations(limit=-1)

        assert result == []
        mock_filter.assert_not_called()
