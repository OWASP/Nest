"""Tests for Certificate GraphQL node."""

from unittest.mock import Mock

from apps.owasp.api.internal.nodes.certificate import CertificateNode
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestCertificateNode(GraphQLNodeBaseTest):
    """Test cases for CertificateNode class."""

    def test_node_fields(self):
        """Test node has expected fields."""
        field_names = {field.name for field in CertificateNode.__strawberry_definition__.fields}
        expected_field_names = {
            "github_user",
            "id",
            "is_verified",
            "issued_at",
            "score",
            "tier",
        }
        assert field_names == expected_field_names

    def test_tier_resolver(self):
        """Test tier resolver returns human-readable display name."""
        mock_cert = Mock()
        mock_cert.get_tier_display.return_value = "Level 1"

        field = self._get_field_by_name("tier", CertificateNode)
        result = field.base_resolver.wrapped_func(None, mock_cert)

        assert result == "Level 1"
        mock_cert.get_tier_display.assert_called_once()

    def test_is_verified_resolver_active(self):
        """Test is_verified returns True when certificate is verified."""
        mock_cert = Mock()
        mock_cert.is_verified = True

        field = self._get_field_by_name("is_verified", CertificateNode)
        result = field.base_resolver.wrapped_func(None, mock_cert)

        assert result is True

    def test_is_verified_resolver_not_verified(self):
        """Test is_verified returns False when certificate is not verified."""
        mock_cert = Mock()
        mock_cert.is_verified = False

        field = self._get_field_by_name("is_verified", CertificateNode)
        result = field.base_resolver.wrapped_func(None, mock_cert)

        assert result is False

    def test_github_user_resolver(self):
        """Test github_user resolver returns the related github_user instance."""
        mock_user = Mock()
        mock_cert = Mock()
        mock_cert.github_user = mock_user

        field = self._get_field_by_name("github_user", CertificateNode)
        result = field.base_resolver.wrapped_func(None, mock_cert)

        assert result == mock_user
