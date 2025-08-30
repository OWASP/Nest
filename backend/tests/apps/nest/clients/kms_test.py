"""Test cases for AWS KMS client."""

from unittest.mock import Mock, patch

import pytest
from django.test.utils import override_settings

from apps.nest.clients.kms import KmsClient


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
