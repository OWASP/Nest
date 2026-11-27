from datetime import timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from django.db.utils import IntegrityError
from django.utils import timezone

from apps.api.internal.mutations.api_key import (
    ApiKeyMutations,
    CreateApiKeyResult,
    RevokeApiKeyResult,
)
from apps.api.models.api_key import MAX_ACTIVE_KEYS, MAX_WORD_LENGTH, ApiKey


def mock_info() -> MagicMock:
    """Return a mocked Info object."""
    info = MagicMock()
    info.context = MagicMock()
    info.context.request = MagicMock()
    info.context.request.user = MagicMock()
    info.context.request.user.is_authenticated = True
    info.context.request.user.pk = 1
    return info


class TestApiKeyMutations:
    """Test cases for the ApiKeyMutations class."""

    @pytest.fixture
    def api_key_mutations(self) -> ApiKeyMutations:
        """Pytest fixture to return an instance of the mutation class."""
        return ApiKeyMutations()

    @patch("apps.api.internal.mutations.api_key.ApiKey.create")
    def test_create_api_key_success(self, mock_api_key_create, api_key_mutations):
        """Test the successful creation of an API key."""
        info = mock_info()
        user = info.context.request.user
        name = "My New App Key"
        expires_at = timezone.now() + timedelta(days=30)
        raw_key = "a_super_secret_and_randomly_generated_key"

        mock_instance = MagicMock(spec=ApiKey)
        mock_api_key_create.return_value = (mock_instance, raw_key)

        result = api_key_mutations.create_api_key(info, name=name, expires_at=expires_at)

        mock_api_key_create.assert_called_once_with(user=user, name=name, expires_at=expires_at)

        assert isinstance(result, CreateApiKeyResult)
        assert result.ok
        assert result.code == "SUCCESS"
        assert result.message == "API key created successfully."
        assert result.api_key == mock_instance
        assert result.raw_key == raw_key

    @patch("apps.api.internal.mutations.api_key.ApiKey.create", return_value=None)
    def test_create_api_key_limit_reached(self, mock_api_key_create, api_key_mutations):
        """Test creating an API key when the user has reached their active key limit."""
        info = mock_info()
        user = info.context.request.user
        name = "This key should not be created"
        expires_at = timezone.now() + timedelta(days=30)

        result = api_key_mutations.create_api_key(info, name=name, expires_at=expires_at)

        mock_api_key_create.assert_called_once_with(user=user, name=name, expires_at=expires_at)

        assert isinstance(result, CreateApiKeyResult)
        assert not result.ok
        assert result.code == "LIMIT_REACHED"
        assert result.message == f"You can have at most {MAX_ACTIVE_KEYS} active API keys."
        assert result.api_key is None
        assert result.raw_key is None

    @patch("apps.api.internal.mutations.api_key.ApiKey.create", side_effect=IntegrityError)
    @patch("apps.api.internal.mutations.api_key.logger")
    def test_create_api_key_integrity_error(
        self, mock_logger, mock_api_key_create, api_key_mutations
    ):
        """Test the mutation's behavior when an IntegrityError is raised."""
        info = mock_info()
        name = "A key that causes a DB error"
        expires_at = timezone.now() + timedelta(days=30)

        result = api_key_mutations.create_api_key(info, name=name, expires_at=expires_at)

        mock_api_key_create.assert_called_once()
        mock_logger.warning.assert_called_once()

        assert isinstance(result, CreateApiKeyResult)
        assert not result.ok
        assert result.code == "ERROR"
        assert result.message == "Something went wrong."
        assert result.api_key is None
        assert result.raw_key is None

    @patch("apps.api.internal.mutations.api_key.ApiKey.objects.get")
    def test_revoke_api_key_success(self, mock_objects_get, api_key_mutations):
        """Test the successful revocation of an existing API key."""
        info = mock_info()
        user = info.context.request.user
        uuid_to_revoke = uuid4()

        mock_api_key = MagicMock(spec=ApiKey)
        mock_objects_get.return_value = mock_api_key

        result = api_key_mutations.revoke_api_key(info, uuid=uuid_to_revoke)

        mock_objects_get.assert_called_once_with(uuid=uuid_to_revoke, user=user)

        assert mock_api_key.is_revoked
        mock_api_key.save.assert_called_once_with(update_fields=("is_revoked", "updated_at"))

        assert isinstance(result, RevokeApiKeyResult)
        assert result.ok
        assert result.code == "SUCCESS"
        assert result.message == "API key revoked successfully."

    @patch(
        "apps.api.internal.mutations.api_key.ApiKey.objects.get",
        side_effect=ApiKey.DoesNotExist,
    )
    @patch("apps.api.internal.mutations.api_key.logger")
    def test_revoke_api_key_not_found(self, mock_logger, mock_objects_get, api_key_mutations):
        """Test revoking a key that does not exist or belong to the user."""
        info = mock_info()
        user = info.context.request.user
        non_existent_public_id = uuid4()

        result = api_key_mutations.revoke_api_key(info, uuid=non_existent_public_id)

        mock_objects_get.assert_called_once_with(uuid=non_existent_public_id, user=user)

        mock_logger.warning.assert_called_once_with("API Key does not exist")

        assert isinstance(result, RevokeApiKeyResult)
        assert not result.ok
        assert result.code == "NOT_FOUND"
        assert result.message == "API key not found."

    def test_create_api_key_empty_name(self, api_key_mutations):
        """Test creating an API key with empty name."""
        info = mock_info()
        name = ""
        expires_at = timezone.now() + timedelta(days=30)

        result = api_key_mutations.create_api_key(info, name=name, expires_at=expires_at)

        assert isinstance(result, CreateApiKeyResult)

        expected = {
            "ok": False,
            "code": "INVALID_NAME",
            "message": "Name is required",
            "api_key": None,
            "raw_key": None,
        }

        for key, value in expected.items():
            assert getattr(result, key) == value

    def test_create_api_key_whitespace_only_name(self, api_key_mutations):
        """Test creating an API key with whitespace-only name."""
        info = mock_info()
        name = "   "
        expires_at = timezone.now() + timedelta(days=30)

        result = api_key_mutations.create_api_key(info, name=name, expires_at=expires_at)

        assert isinstance(result, CreateApiKeyResult)

        expected = {
            "ok": False,
            "code": "INVALID_NAME",
            "message": "Name is required",
            "api_key": None,
            "raw_key": None,
        }

        for field, value in expected.items():
            assert getattr(result, field) == value

    def test_create_api_key_name_too_long(self, api_key_mutations):
        """Test creating an API key with name exceeding maximum length."""
        info = mock_info()
        name = "a" * (MAX_WORD_LENGTH + 1)
        expires_at = timezone.now() + timedelta(days=30)

        result = api_key_mutations.create_api_key(info, name=name, expires_at=expires_at)

        assert isinstance(result, CreateApiKeyResult)

        expected = {
            "ok": False,
            "code": "INVALID_NAME",
            "message": "Name too long",
            "api_key": None,
            "raw_key": None,
        }

        for field, value in expected.items():
            assert getattr(result, field) == value

    def test_create_api_key_expires_in_past(self, api_key_mutations):
        """Test creating an API key with expiry date in the past."""
        info = mock_info()
        name = "Valid Name"
        expires_at = timezone.now() - timedelta(days=1)

        result = api_key_mutations.create_api_key(info, name=name, expires_at=expires_at)

        assert isinstance(result, CreateApiKeyResult)

        expected = {
            "ok": False,
            "code": "INVALID_DATE",
            "message": "Expiry date must be in future",
            "api_key": None,
            "raw_key": None,
        }

        for field, value in expected.items():
            assert getattr(result, field) == value
