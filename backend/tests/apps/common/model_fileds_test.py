"""Test cases for common custom model fields."""

import pytest
from django.test import override_settings

from apps.common.model_fields import KmsEncryptedField


class TestKmsEncryptedField:
    """Test cases for KmsEncryptedField."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.field = KmsEncryptedField()

    @override_settings(IS_AWS_KMS_ENABLED=False)
    def test_get_prep_value_without_kms(self):
        """Test get_prep_value without KMS."""
        with pytest.raises(ValueError, match="AWS KMS is not enabled."):
            self.field.get_prep_value("test")

    @override_settings(IS_AWS_KMS_ENABLED=False)
    def test_to_python_without_kms(self):
        """Test to_python without KMS."""
        with pytest.raises(ValueError, match="AWS KMS is not enabled."):
            self.field.to_python(b"encrypted_value")
