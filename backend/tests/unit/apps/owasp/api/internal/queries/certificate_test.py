from unittest.mock import MagicMock, patch

import pytest

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

    @patch("apps.owasp.models.crp.certificate.Certificate.objects.select_related")
    def test_certificate_not_found(self, mock_select_related):
        """Test certificate resolution returns None when a well-formed ID does not exist."""
        mock_select_related.return_value.get.side_effect = Certificate.DoesNotExist

        result = CertificateQuery().certificate("CERT12345678")

        mock_select_related.return_value.get.assert_called_once_with(id="CERT12345678")
        assert result is None

    @pytest.mark.parametrize(
        "certificate_id",
        [
            "",
            "INVALID_ID",
            "cert12345678",
            "CERT1234567",
            "CERT123456789",
            "CERT-1234567",
        ],
    )
    @patch("apps.owasp.models.crp.certificate.Certificate.objects.select_related")
    def test_certificate_malformed_id_skips_query(self, mock_select_related, certificate_id):
        """Test malformed certificate IDs return None without touching the database."""
        result = CertificateQuery().certificate(certificate_id)

        assert result is None
        mock_select_related.assert_not_called()

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
