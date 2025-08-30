"""AWS KMS client."""

import boto3
from django.conf import settings


class KmsClient:
    """AWS KMS Client."""

    def __init__(self):
        """Initialize the KMS client."""
        self.client = boto3.client(
            "kms",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

    def decrypt(self, text: bytes) -> str:
        """Decrypt the ciphertext using KMS."""
        return self.client.decrypt(
            CiphertextBlob=text,
        )["Plaintext"].decode("utf-8")

    def encrypt(self, text: str) -> bytes:
        """Encrypt the plaintext using KMS."""
        return self.client.encrypt(
            KeyId=settings.AWS_KMS_KEY_ID,
            Plaintext=text.encode("utf-8"),
        )["CiphertextBlob"]


_kms_client = None


def get_kms_client() -> KmsClient:
    """Get the AWS KMS client."""
    global _kms_client  # noqa: PLW0603
    if _kms_client is None:
        _kms_client = KmsClient()
    return _kms_client
