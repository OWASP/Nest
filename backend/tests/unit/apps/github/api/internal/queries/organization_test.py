"""Test cases for OrganizationQuery."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

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

    @patch("apps.github.models.organization.Organization.objects.aget", new_callable=AsyncMock)
    def test_organization_found(self, mock_aget, mock_organization):
        """Test fetching organization when it exists."""
        mock_aget.return_value = mock_organization

        result = asyncio.run(OrganizationQuery().organization(login="owasp"))

        assert result == mock_organization
        mock_aget.assert_called_once_with(is_owasp_related_organization=True, login="owasp")

    @patch("apps.github.models.organization.Organization.objects.aget", new_callable=AsyncMock)
    def test_organization_not_found(self, mock_aget):
        """Test fetching organization when it doesn't exist."""
        mock_aget.side_effect = Organization.DoesNotExist()

        result = asyncio.run(OrganizationQuery().organization(login="nonexistent"))

        assert result is None
        mock_aget.assert_called_once_with(is_owasp_related_organization=True, login="nonexistent")

    @patch("apps.github.models.organization.Organization.objects.aget", new_callable=AsyncMock)
    def test_organization_with_different_login(self, mock_aget, mock_organization):
        """Test fetching organization with different login."""
        mock_aget.return_value = mock_organization

        result = asyncio.run(OrganizationQuery().organization(login="test-org"))

        assert result == mock_organization
        mock_aget.assert_called_once_with(is_owasp_related_organization=True, login="test-org")
