import hashlib
import secrets
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from apps.nest.models.api_key import MAX_ACTIVE_KEYS, APIKey


@pytest.fixture
def mock_user():
    """Pytest fixture to create a mock user object."""
    user = MagicMock()
    user.pk = 1
    return user


class TestAPIKeyModel:
    """Test suite for the APIKey model."""

    def test_generate_raw_key(self):
        """Test that generate_raw_key."""
        raw_key = APIKey.generate_raw_key()
        assert isinstance(raw_key, str)
        assert len(raw_key) > 32
        assert secrets.token_urlsafe(32) != secrets.token_urlsafe(32)

    def test_generate_hash_key(self):
        """Test that generate_hash_key."""
        raw_key = "test_key_123"
        expected_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        generated_hash = APIKey.generate_hash_key(raw_key)
        assert generated_hash == expected_hash
        assert isinstance(generated_hash, str)
        assert len(generated_hash) == 64

    @patch("apps.nest.models.APIKey.objects.create")
    @patch("apps.nest.models.APIKey.active_count_for_user", return_value=1)
    def test_create_success(self, mock_active_count, mock_create, mock_user):
        """Test successful creation of an API key."""
        name = "Test Key"
        expires_at = timezone.now() + timedelta(days=30)

        mock_instance = MagicMock()
        mock_create.return_value = mock_instance

        with patch(
            "apps.nest.models.APIKey.generate_raw_key",
            return_value="a_very_secure_random_string_1234",
        ):
            instance, raw_key = APIKey.create(user=mock_user, name=name, expires_at=expires_at)

            assert instance is not None
            assert raw_key is not None
            mock_active_count.assert_called_once_with(mock_user)
            mock_create.assert_called_once()

            call_args = mock_create.call_args[1]
            assert call_args["user"] == mock_user
            assert call_args["name"] == name
            assert call_args["key_suffix"] == "1234"
            assert "hash" in call_args

    @patch("apps.nest.models.APIKey.active_count_for_user", return_value=MAX_ACTIVE_KEYS)
    def test_create_failure_max_keys_reached(self, mock_active_count, mock_user):
        """Test that key creation fails when the user has reached the max active key limit."""
        result = APIKey.create(user=mock_user, name="Another Key")
        assert result is None
        mock_active_count.assert_called_once_with(mock_user)

    @patch("apps.nest.models.APIKey.objects")
    def test_active_count_for_user(self, mock_objects, mock_user):
        """Test the `active_count_for_user` method with proper filtering."""
        mock_objects.filter.return_value.filter.return_value.count.return_value = 3

        count = APIKey.active_count_for_user(mock_user)

        assert count == 3
        user_filter_call = mock_objects.filter.call_args_list[0][1]
        assert user_filter_call["user"] == mock_user
        assert user_filter_call["is_revoked"] is False

        expiry_filter_call = mock_objects.filter.return_value.filter.call_args_list[0][0][0]
        assert "expires_at__isnull" in str(expiry_filter_call)
        assert "expires_at__gt" in str(expiry_filter_call)

    @patch("apps.nest.models.APIKey.objects.get")
    def test_authenticate_success(self, mock_get):
        """Test successful authentication with a valid raw key."""
        raw_key = "valid_key"
        mock_api_key = MagicMock(spec=APIKey)
        mock_api_key.is_valid.return_value = True
        mock_get.return_value = mock_api_key

        result = APIKey.authenticate(raw_key)

        assert result is mock_api_key
        mock_api_key.is_valid.assert_called_once()
        mock_get.assert_called_once()

    @patch("apps.nest.models.APIKey.objects.get")
    def test_authenticate_failure_invalid_key(self, mock_get):
        """Test authentication failure when the key is not valid (e.g., revoked)."""
        raw_key = "invalid_key"
        mock_api_key = MagicMock(spec=APIKey)
        mock_api_key.is_valid.return_value = False
        mock_get.return_value = mock_api_key

        result = APIKey.authenticate(raw_key)

        assert result is None
        mock_api_key.is_valid.assert_called_once()

    @patch("apps.nest.models.APIKey.objects.get", side_effect=APIKey.DoesNotExist)
    def test_authenticate_failure_does_not_exist(self, mock_get):
        """Test authentication failure when the key does not exist."""
        raw_key = "non_existent_key"
        result = APIKey.authenticate(raw_key)
        assert result is None
        mock_get.assert_called_once()

    def test_is_valid_active_key(self):
        """Test that a non-revoked, non-expired key is valid."""
        key = APIKey(is_revoked=False, expires_at=None)
        assert key.is_valid() is True

    def test_is_valid_revoked_key(self):
        """Test that a revoked key is not valid."""
        key = APIKey(is_revoked=True, expires_at=None)
        assert key.is_valid() is False

    def test_str_representation_active(self):
        """Test the string representation of an active key."""
        key = APIKey(name="My Active Key", is_revoked=False)
        assert str(key) == "My Active Key (active)"

    def test_str_representation_revoked(self):
        """Test the string representation of a revoked key."""
        key = APIKey(name="My Revoked Key", is_revoked=True)
        assert str(key) == "My Revoked Key (revoked)"
