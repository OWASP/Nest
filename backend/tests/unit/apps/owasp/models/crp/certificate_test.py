from unittest.mock import MagicMock, patch

import pytest

from apps.github.models.user import User
from apps.owasp.exceptions import CertificateIssuanceError
from apps.owasp.models.crp.certificate import (
    CERTIFICATE_ID_ALPHABET,
    CERTIFICATE_ID_LENGTH,
    Certificate,
    generate_certificate_id,
)
from apps.owasp.models.crp.recognition_enums import TierChoices

MODEL_PATH = "apps.owasp.models.crp.certificate"


class TestCertificateModel:
    """Test suite for Certificate model."""

    def test_generate_certificate_id(self):
        """Test generate_certificate_id produces a 12-char string from ALPHABET."""
        cert_id = generate_certificate_id()
        assert len(cert_id) == CERTIFICATE_ID_LENGTH
        assert all(c in CERTIFICATE_ID_ALPHABET for c in cert_id)

    def test_str_representation_active(self):
        """Test __str__ for active certificate."""
        user = User(login="john_doe")
        cert = Certificate(github_user=user, tier=TierChoices.LEVEL_1, is_revoked=False)

        assert str(cert) == "john_doe - LEVEL_1 Certificate (Active)"

    def test_str_representation_revoked(self):
        """Test __str__ for revoked certificate."""
        user = User(login="jane_doe")
        cert = Certificate(github_user=user, tier=TierChoices.LEVEL_2, is_revoked=True)

        assert str(cert) == "jane_doe - LEVEL_2 Certificate (Revoked)"

    @patch("django.db.transaction.Atomic.__enter__", return_value=None)
    @patch("django.db.transaction.Atomic.__exit__", return_value=None)
    @patch(f"{MODEL_PATH}.Certificate.objects")
    @patch(f"{MODEL_PATH}.User.objects")
    def test_issue_certificate_already_exists(
        self, mock_user_objects, mock_cert_objects, mock_exit, mock_enter
    ):
        """Test issue_certificate returns early if active certificate already exists."""
        user = User(id=1, login="john_doe")
        mock_user_objects.select_for_update.return_value.get.return_value = user
        mock_cert_objects.filter.return_value.exists.return_value = True

        Certificate.issue_certificate(user, 150, TierChoices.LEVEL_2)

        mock_cert_objects.filter.assert_called_once_with(
            github_user=user, tier=TierChoices.LEVEL_2, is_revoked=False
        )

    @patch("django.db.transaction.Atomic.__enter__", return_value=None)
    @patch("django.db.transaction.Atomic.__exit__", return_value=None)
    @patch(f"{MODEL_PATH}.Certificate.objects")
    @patch(f"{MODEL_PATH}.CertificateProviderFactory")
    @patch(f"{MODEL_PATH}.User.objects")
    def test_issue_certificate_provider_resolution_error(
        self, mock_user_objects, mock_factory, mock_cert_objects, mock_exit, mock_enter
    ):
        """Test issue_certificate raises on provider resolution error."""
        user = User(id=1, login="john_doe")
        mock_user_objects.select_for_update.return_value.get.return_value = user
        mock_cert_objects.filter.return_value.exists.return_value = False
        mock_factory.get_provider.side_effect = ValueError("Unknown provider")

        with pytest.raises(CertificateIssuanceError):
            Certificate.issue_certificate(user, 150, TierChoices.LEVEL_2)

    @patch("django.db.transaction.Atomic.__enter__", return_value=None)
    @patch("django.db.transaction.Atomic.__exit__", return_value=None)
    @patch(f"{MODEL_PATH}.Certificate.objects")
    @patch(f"{MODEL_PATH}.CertificateProviderFactory")
    @patch(f"{MODEL_PATH}.User.objects")
    def test_issue_certificate_provider_issuance_exception(
        self, mock_user_objects, mock_factory, mock_cert_objects, mock_exit, mock_enter
    ):
        """Test issue_certificate raises when provider issuance fails."""
        user = User(id=1, login="test_user")
        mock_user_objects.select_for_update.return_value.get.return_value = user
        mock_cert_objects.filter.return_value.exists.return_value = False

        mock_provider = MagicMock()
        mock_provider.issue_certificate.side_effect = RuntimeError("PDF generation failed")
        mock_factory.get_provider.return_value = mock_provider

        with pytest.raises(CertificateIssuanceError):
            Certificate.issue_certificate(user, 150, TierChoices.LEVEL_2)

    @patch("django.db.transaction.Atomic.__enter__", return_value=None)
    @patch("django.db.transaction.Atomic.__exit__", return_value=None)
    @patch(f"{MODEL_PATH}.Certificate.objects")
    @patch(f"{MODEL_PATH}.CertificateProviderFactory")
    @patch(f"{MODEL_PATH}.User.objects")
    def test_issue_certificate_success(
        self, mock_user_objects, mock_factory, mock_cert_objects, mock_exit, mock_enter
    ):
        """Test successful certificate issuance."""
        user = User(id=1, login="test_user")
        mock_user_objects.select_for_update.return_value.get.return_value = user
        mock_cert_objects.filter.return_value.exists.return_value = False

        mock_provider = MagicMock()
        mock_factory.get_provider.return_value = mock_provider

        Certificate.issue_certificate(user, 150, TierChoices.LEVEL_2)

        mock_provider.issue_certificate.assert_called_once_with(user, 150, TierChoices.LEVEL_2)
