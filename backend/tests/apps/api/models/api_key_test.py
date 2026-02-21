import hashlib
import secrets
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from apps.api.models.api_key import ApiKey

USER_ACTIVE_KEYS_PATH = "apps.nest.models.user.User.active_api_keys"


@pytest.fixture
def mock_user():
    """Pytest fixture to create a mock user object with a mocked property."""
    user = MagicMock()
    user.pk = 1
    return user


class TestApiKeyModel:
    """Test suite for the ApiKey model."""

    def test_generate_raw_key(self):
        """Test that generate_raw_key creates a sufficiently long, random string."""
        raw_key = ApiKey.generate_raw_key()
        assert isinstance(raw_key, str)
        assert len(raw_key) > 40
        assert secrets.token_urlsafe(32) != secrets.token_urlsafe(32)

    def test_generate_hash_key(self):
        """Test that generate_hash_key produces a correct SHA-256 hash."""
        raw_key = "test_key_123"
        expected_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        generated_hash = ApiKey.generate_hash_key(raw_key)
        assert generated_hash == expected_hash
        assert isinstance(generated_hash, str)
        assert len(generated_hash) == 64

    @patch("apps.api.models.api_key.ApiKey.objects.filter")
    @patch("apps.api.models.api_key.ApiKey.objects.get")
    def test_authenticate_success(self, mock_get, mock_filter):
        """Test successful authentication with a valid raw key."""
        raw_key = "valid_key"
        mock_api_key = MagicMock(spec=ApiKey)
        mock_api_key.is_valid = True
        mock_get.return_value = mock_api_key

        mock_filter.return_value.update.return_value = 1

        result = ApiKey.authenticate(raw_key)

        assert result is mock_api_key
        mock_get.assert_called_once()
        mock_filter.assert_called_once_with(pk=mock_api_key.pk)
        mock_filter.return_value.update.assert_called_once()

    @patch("apps.api.models.api_key.ApiKey.objects.get")
    def test_authenticate_failure_invalid_key(self, mock_get):
        """Test authentication failure when the key is not valid."""
        raw_key = "invalid_key"
        mock_api_key = MagicMock(spec=ApiKey)
        mock_api_key.is_valid = False
        mock_get.return_value = mock_api_key

        result = ApiKey.authenticate(raw_key)

        assert result is None

    @patch("apps.api.models.api_key.ApiKey.objects.get", side_effect=ApiKey.DoesNotExist)
    def test_authenticate_failure_does_not_exist(self, mock_get):
        """Test authentication failure when the key does not exist."""
        raw_key = "non_existent_key"
        result = ApiKey.authenticate(raw_key)
        assert result is None
        mock_get.assert_called_once()

    def test_is_valid_active_key(self):
        """Test that a non-revoked, non-expired key is valid."""
        key = ApiKey(is_revoked=False, expires_at=timezone.now() + timedelta(days=1))
        assert key.is_valid

    def test_is_valid_expired_key(self):
        """Test that an expired key is not valid."""
        key = ApiKey(is_revoked=False, expires_at=timezone.now() - timedelta(days=1))
        assert not key.is_valid

    def test_is_valid_revoked_key(self):
        """Test that a revoked key is not valid."""
        key = ApiKey(is_revoked=True, expires_at=timezone.now() + timedelta(days=1))
        assert not key.is_valid

    def test_str_representation_active(self):
        """Test the string representation of an active key."""
        key = ApiKey(name="My Active Key", is_revoked=False)
        assert str(key) == "My Active Key (active)"

    def test_str_representation_revoked(self):
        """Test the string representation of a revoked key."""
        key = ApiKey(name="My Revoked Key", is_revoked=True)
        assert str(key) == "My Revoked Key (revoked)"

    @patch("apps.api.models.api_key.User")
    @patch("apps.api.models.api_key.transaction")
    @patch("apps.api.models.api_key.ApiKey.objects.create")
    @patch("apps.api.models.api_key.ApiKey.generate_hash_key", return_value="hashed_key")
    @patch("apps.api.models.api_key.ApiKey.generate_raw_key", return_value="raw_key_123")
    def test_create_success(
        self,
        mock_raw_key,
        mock_hash_key,
        mock_create,
        mock_transaction,
        mock_user_model,
        mock_user,
    ):
        """Test successful API key creation."""
        mock_transaction.atomic = lambda: MagicMock(
            __enter__=MagicMock(return_value=None),
            __exit__=MagicMock(return_value=False),
        )
        mock_locked_user = MagicMock()
        mock_locked_user.active_api_keys.count.return_value = 0
        mock_user_model.objects.select_for_update.return_value.get.return_value = mock_locked_user
        mock_instance = MagicMock(spec=ApiKey)
        mock_create.return_value = mock_instance
        expires_at = timezone.now() + timedelta(days=30)

        result = ApiKey.create.__wrapped__(ApiKey, mock_user, "Test Key", expires_at)

        assert result == (mock_instance, "raw_key_123")
        mock_create.assert_called_once_with(
            expires_at=expires_at,
            hash="hashed_key",
            name="Test Key",
            user=mock_locked_user,
        )

    @patch("apps.api.models.api_key.User")
    @patch("apps.api.models.api_key.transaction")
    def test_create_max_keys_exceeded(self, mock_transaction, mock_user_model, mock_user):
        """Test API key creation fails when max active keys exceeded."""
        mock_transaction.atomic = lambda: MagicMock(
            __enter__=MagicMock(return_value=None),
            __exit__=MagicMock(return_value=False),
        )
        mock_locked_user = MagicMock()
        mock_locked_user.active_api_keys.count.return_value = 100
        mock_user_model.objects.select_for_update.return_value.get.return_value = mock_locked_user
        expires_at = timezone.now() + timedelta(days=30)

        result = ApiKey.create.__wrapped__(ApiKey, mock_user, "Test Key", expires_at)

        assert result is None
