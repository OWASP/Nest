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
