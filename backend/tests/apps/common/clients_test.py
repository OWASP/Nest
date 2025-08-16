"""Test cases for API clients."""

from unittest.mock import Mock, patch

import pytest
from django.test.utils import override_settings

from apps.common.clients import KmsClient, get_google_auth_client, get_kms_client


class TestKmsClient:
    """Test cases for KMS client."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up mock KMS client."""
        with patch("boto3.client") as mock_boto3_client:
            self.mock_boto3_client = mock_boto3_client
            self.mock_kms_client = Mock()
            self.mock_boto3_client.return_value = self.mock_kms_client
            self.kms_client = KmsClient()

    @override_settings(AWS_REGION="us-west-2", AWS_KMS_KEY_ID="test_key_id")
    def test_encrypt(self):
        """Test encryption."""
        plaintext = "test"
        self.mock_kms_client.encrypt.return_value = {"CiphertextBlob": b"encrypted"}
        ciphertext = self.kms_client.encrypt(plaintext)
        assert ciphertext != plaintext
        self.mock_kms_client.encrypt.assert_called_once_with(
            Plaintext=plaintext.encode("utf-8"), KeyId="test_key_id"
        )

    @override_settings(AWS_REGION="us-west-2", AWS_KMS_KEY_ID="test_key_id")
    def test_decrypt(self):
        """Test decryption."""
        self.mock_kms_client.decrypt.return_value = {"Plaintext": b"test"}
        decrypted = self.kms_client.decrypt(b"encrypted")
        assert decrypted == "test"
        self.mock_kms_client.decrypt.assert_called_once_with(CiphertextBlob=b"encrypted")

    @override_settings(AWS_REGION="us-west-2", AWS_KMS_KEY_ID="test_key_id")
    def test_get_kms_client(self):
        """Test getting the KMS client."""
        client1 = get_kms_client()
        client2 = get_kms_client()
        assert client1 is client2, "KMS client should be a singleton."
        assert isinstance(client1, KmsClient), "Should return an instance of KmsClient."


@override_settings(
    IS_GOOGLE_AUTH_ENABLED=True,
    GOOGLE_AUTH_CLIENT_ID="test_client_id",
    GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
    GOOGLE_AUTH_REDIRECT_URI="test_redirect_uri",
)
@patch("apps.common.clients.Flow.from_client_config")
def test_google_auth_client(mock_from_client_config):
    """Test getting the Google OAuth client."""
    mock_from_client_config.return_value = Mock()
    client = get_google_auth_client()
    assert client is not None, "Google OAuth client should not be None."
    mock_from_client_config.assert_called_once_with(
        client_config={
            "web": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "redirect_uris": ["test_redirect_uri"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
    )
