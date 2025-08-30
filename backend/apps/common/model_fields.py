"""Custom fields for Django models."""

from django.conf import settings
from django.db import models

from apps.nest.clients.kms import kms_client

KMS_ERROR_MESSAGE = "AWS KMS is not enabled."
STR_ERROR_MESSAGE = "Value must be a string to encrypt."
BYTES_ERROR_MESSAGE = "Value must be bytes or bytearray to decrypt."


class KmsEncryptedField(models.BinaryField):
    """Custom field for KMS encrypted data."""

    description = "Encrypted data using AWS KMS."

    def get_prep_value(self, value):
        """Encrypt the value using KMS."""
        if not settings.IS_AWS_KMS_ENABLED:
            raise ValueError(KMS_ERROR_MESSAGE)
        if not value:
            return None
        if not isinstance(value, str):
            raise TypeError(STR_ERROR_MESSAGE)
        ciphertext = kms_client.encrypt(value)
        return super().get_prep_value(ciphertext)

    def _get_from_db_helper(self, value):
        """Decrypt the value from the database using KMS."""
        if value in (None, b"", bytearray(), memoryview(b"")):
            return None
        if not settings.IS_AWS_KMS_ENABLED:
            raise ValueError(KMS_ERROR_MESSAGE)
        if isinstance(value, str):
            return value
        if not isinstance(value, (bytes, bytearray, memoryview)):
            raise TypeError(BYTES_ERROR_MESSAGE)
        return kms_client.decrypt(bytes(value)) if value else None

    def from_db_value(self, value, expression, connection):
        """Decrypt the value from the database using KMS."""
        return self._get_from_db_helper(value)

    def to_python(self, value):
        """Decrypt the value using KMS."""
        return self._get_from_db_helper(value)
