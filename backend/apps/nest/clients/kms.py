"""AWS KMS client."""

from threading import Lock

import boto3
from django.conf import settings


class KmsClient:
    """AWS KMS Client."""

    _lock = Lock()

    def __new__(cls):
        """Create a new instance of KmsClient."""
        if not hasattr(cls, "instance"):
            with cls._lock:
                if not hasattr(cls, "instance"):
                    cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        """Initialize the KMS client."""
        if getattr(self, "client", None) is not None:
            return
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
