from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError

from apps.owasp.api.internal.queries.certificate import CertificateQuery
from apps.owasp.models.crp.certificate import Certificate


class TestCertificateQuery:
    """Test suite for CertificateQuery."""

    def test_has_strawberry_definition(self):
        """Test that CertificateQuery has valid Strawberry field definitions."""
        assert hasattr(CertificateQuery, "__strawberry_definition__")
        field_names = [field.name for field in CertificateQuery.__strawberry_definition__.fields]
        assert "certificate" in field_names
        assert "my_certificates" in field_names

    @patch("apps.owasp.models.crp.certificate.Certificate.objects.select_related")
    def test_certificate_found(self, mock_select_related):
        """Test certificate resolution when certificate exists."""
        mock_cert = MagicMock(spec=Certificate)
        mock_select_related.return_value.get.return_value = mock_cert

        result = CertificateQuery().certificate("CERT12345678")

        mock_select_related.assert_called_once_with("chapter", "issuer", "project", "recipient")
        mock_select_related.return_value.get.assert_called_once_with(id="CERT12345678")
        assert result == mock_cert

    @pytest.mark.parametrize(
        "exception",
        [
            Certificate.DoesNotExist(),
            ValidationError("Invalid ID format"),
            ValueError("Invalid value"),
        ],
    )
    @patch("apps.owasp.models.crp.certificate.Certificate.objects.select_related")
    def test_certificate_not_found_or_invalid(self, mock_select_related, exception):
        """Test certificate resolution returns None when not found or on validation error."""
        mock_select_related.return_value.get.side_effect = exception

        result = CertificateQuery().certificate("INVALID_ID")

        assert result is None

    def test_my_certificates_user_without_github_user(self):
        """Test my_certificates returns empty list when user has no github_user."""
        info = MagicMock()
        info.context.request.user = MagicMock(spec=[])  # user has no github_user attr

        result = CertificateQuery().my_certificates(info)

        assert result == []

    @patch("apps.owasp.models.crp.certificate.Certificate.objects.select_related")
    def test_my_certificates_returns_active_certificates(self, mock_select_related):
        """Test my_certificates returns the user's active certificates."""
        info = MagicMock()
        mock_github_user = MagicMock()
        info.context.request.user.github_user = mock_github_user

        mock_certs = [MagicMock(spec=Certificate)]
        mock_qs = MagicMock()
        mock_select_related.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.order_by.return_value = mock_certs

        result = CertificateQuery().my_certificates(info)

        mock_select_related.assert_called_once_with("chapter", "issuer", "project", "recipient")
        mock_qs.filter.assert_called_once_with(recipient=mock_github_user, is_revoked=False)
        mock_qs.order_by.assert_called_once_with("-issued_at")
        assert result == mock_certs
