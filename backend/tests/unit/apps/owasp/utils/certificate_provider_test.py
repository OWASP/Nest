from unittest.mock import MagicMock, patch

import pytest

from apps.owasp.models.crp.recognition_enums import TierChoices
from apps.owasp.utils.certificate_provider import (
    CertificateProviderFactory,
    LocalCertificateProvider,
)


class TestLocalCertificateProvider:
    """Test suite for LocalCertificateProvider."""

    @patch("apps.owasp.models.crp.certificate.Certificate.objects.create")
    def test_issue_certificate_creates_record(self, mock_create):
        """Test issue_certificate creates a Certificate record in local DB."""
        mock_user = MagicMock()
        provider = LocalCertificateProvider()

        provider.issue_certificate(mock_user, 200, TierChoices.LEVEL_2)

        mock_create.assert_called_once_with(
            recipient=mock_user,
            score=200,
            tier=TierChoices.LEVEL_2,
        )


class TestCertificateProviderFactory:
    """Test suite for CertificateProviderFactory."""

    @patch("apps.owasp.utils.certificate_provider.settings")
    def test_get_provider_local_success(self, mock_settings):
        """Test get_provider returns LocalCertificateProvider when setting is 'local'."""
        mock_settings.CERTIFICATE_PROVIDER = "local"

        provider = CertificateProviderFactory.get_provider()

        assert isinstance(provider, LocalCertificateProvider)

    @patch("apps.owasp.utils.certificate_provider.settings")
    def test_get_provider_unknown_raises_value_error(self, mock_settings):
        """Test get_provider raises ValueError for unknown provider type."""
        mock_settings.CERTIFICATE_PROVIDER = "invalid_provider"

        with pytest.raises(ValueError, match="Unknown certificate provider: invalid_provider"):
            CertificateProviderFactory.get_provider()
