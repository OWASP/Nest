"""Custom fields for Django models."""

from django.conf import settings
from django.db import models

from apps.common.clients import get_kms_client

KMS_ERROR_MESSAGE = "AWS KMS is not enabled."


class KmsEncryptedField(models.BinaryField):
    """Custom field for KMS encrypted data."""

    description = "Encrypted data using AWS KMS."

    def get_prep_value(self, value):
        """Encrypt the value using KMS."""
        if not settings.IS_AWS_KMS_ENABLED:
            raise ValueError(KMS_ERROR_MESSAGE)
        return get_kms_client().encrypt(value) if value else None

    def to_python(self, value):
        """Decrypt the value using KMS."""
        if not settings.IS_AWS_KMS_ENABLED:
            raise ValueError(KMS_ERROR_MESSAGE)
        return get_kms_client().decrypt(value) if value else None
