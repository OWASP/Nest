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

    @override_settings(IS_AWS_KMS_ENABLED=True)
    @pytest.mark.parametrize("value", [None, ""])
    def test_get_prep_value_with_none(self, value):
        """Test get_prep_value with None."""
        result = self.field.get_prep_value(value)
        assert result is None

    @override_settings(IS_AWS_KMS_ENABLED=True)
    @pytest.mark.parametrize("value", [5, b"rabbit", []])
    def test_get_prep_value_with_non_string(self, value):
        """Test get_prep_value with a non-string."""
        with pytest.raises(TypeError, match="Value must be a string to encrypt."):
            self.field.get_prep_value(value)

    @override_settings(IS_AWS_KMS_ENABLED=True)
    @pytest.mark.parametrize("value", [None, b"", bytearray(), memoryview(b"")])
    def test_from_db_value_with_none(self, value):
        """Test from_db_value with None."""
        result = self.field.from_db_value(value, None, None)
        assert result is None

    @override_settings(IS_AWS_KMS_ENABLED=False)
    def test_from_db_value_without_kms(self):
        """Test from_db_value without KMS."""
        with pytest.raises(ValueError, match="AWS KMS is not enabled."):
            self.field.from_db_value(b"encrypted_value", None, None)

    @override_settings(IS_AWS_KMS_ENABLED=True)
    def test_from_db_value_with_string(self):
        """Test from_db_value with a string."""
        result = self.field.from_db_value("value", None, None)
        assert result == "value"

    @override_settings(IS_AWS_KMS_ENABLED=True)
    @pytest.mark.parametrize("value", [55, [], ()])
    def test_from_db_value_with_invalid_type(self, value):
        """Test from_db_value with an invalid type."""
        with pytest.raises(TypeError, match="Value must be bytes or bytearray to decrypt."):
            self.field.from_db_value(value, None, None)

    @override_settings(IS_AWS_KMS_ENABLED=True)
    def test_to_python_with_string(self):
        """Test to_python with a string."""
        result = self.field.to_python("value")
        assert result == "value"

    @override_settings(IS_AWS_KMS_ENABLED=True)
    @pytest.mark.parametrize("value", [55, [], ()])
    def test_to_python_with_invalid_type(self, value):
        """Test to_python with an invalid type."""
        with pytest.raises(TypeError, match="Value must be bytes or bytearray to decrypt."):
            self.field.to_python(value)
