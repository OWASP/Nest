from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.db.utils import IntegrityError
from django.utils import timezone

from apps.nest.graphql.mutations.api_key import (
    APIKeyMutations,
    CreateAPIKeyResult,
    RevokeAPIKeyResult,
)
from apps.nest.models import APIKey


def fake_info() -> MagicMock:
    """Return a mocked Info object."""
    info = MagicMock()
    info.context = MagicMock()
    info.context.request = MagicMock()
    info.context.request.user = MagicMock()
    info.context.request.user.is_authenticated = True
    info.context.request.user.pk = 1
    return info


class TestAPIKeyMutations:
    """Test cases for the APIKeyMutations class."""

    @pytest.fixture
    def api_key_mutations(self) -> APIKeyMutations:
        """Pytest fixture to return an instance of the mutation class."""
        return APIKeyMutations()

    @patch("apps.nest.graphql.mutations.api_key.APIKey.create")
    def test_create_api_key_success(self, mock_api_key_create, api_key_mutations):
        """Test the successful creation of an API key."""
        info = fake_info()
        user = info.context.request.user
        name = "My New App Key"
        expires_at = timezone.now() + timedelta(days=30)
        raw_key = "a_super_secret_and_randomly_generated_key"

        mock_instance = MagicMock(spec=APIKey)
        mock_api_key_create.return_value = (mock_instance, raw_key)

        result = api_key_mutations.create_api_key(info, name=name, expires_at=expires_at)

        mock_api_key_create.assert_called_once_with(user=user, name=name, expires_at=expires_at)

        assert isinstance(result, CreateAPIKeyResult)
        assert result.ok is True
        assert result.code == "SUCCESS"
        assert result.message == "API key created successfully."
        assert result.api_key == mock_instance
        assert result.raw_key == raw_key

    @patch("apps.nest.graphql.mutations.api_key.APIKey.create", return_value=None)
    def test_create_api_key_limit_reached(self, mock_api_key_create, api_key_mutations):
        """Test creating an API key when the user has reached their active key limit."""
        info = fake_info()
        user = info.context.request.user
        name = "This key should not be created"

        result = api_key_mutations.create_api_key(info, name=name)

        mock_api_key_create.assert_called_once_with(user=user, name=name, expires_at=None)

        assert isinstance(result, CreateAPIKeyResult)
        assert result.ok is False
        assert result.code == "LIMIT_REACHED"
        assert result.message == "You can have at most 5 active API keys."
        assert result.api_key is None
        assert result.raw_key is None

    @patch("apps.nest.graphql.mutations.api_key.APIKey.create", side_effect=IntegrityError)
    @patch("apps.nest.graphql.mutations.api_key.logger")
    def test_create_api_key_integrity_error(
        self, mock_logger, mock_api_key_create, api_key_mutations
    ):
        """Test the mutation's behavior when an IntegrityError is raised."""
        info = fake_info()
        name = "A key that causes a DB error"

        result = api_key_mutations.create_api_key(info, name=name)

        mock_api_key_create.assert_called_once()
        mock_logger.warning.assert_called_once()

        assert isinstance(result, CreateAPIKeyResult)
        assert result.ok is False
        assert result.code == "ERROR"
        assert result.message == "Something went wrong."
        assert result.api_key is None
        assert result.raw_key is None

    @patch("apps.nest.graphql.mutations.api_key.APIKey.objects.get")
    def test_revoke_api_key_success(self, mock_objects_get, api_key_mutations):
        """Test the successful revocation of an existing API key."""
        info = fake_info()
        user = info.context.request.user
        key_id_to_revoke = 42

        mock_api_key = MagicMock(spec=APIKey)
        mock_objects_get.return_value = mock_api_key

        result = api_key_mutations.revoke_api_key(info, key_id=key_id_to_revoke)

        mock_objects_get.assert_called_once_with(id=key_id_to_revoke, user=user)

        assert mock_api_key.is_revoked is True
        mock_api_key.save.assert_called_once_with(update_fields=["is_revoked"])

        assert isinstance(result, RevokeAPIKeyResult)
        assert result.ok is True
        assert result.code == "SUCCESS"
        assert result.message == "API key revoked successfully."

    @patch(
        "apps.nest.graphql.mutations.api_key.APIKey.objects.get", side_effect=APIKey.DoesNotExist
    )
    @patch("apps.nest.graphql.mutations.api_key.logger")
    def test_revoke_api_key_not_found(self, mock_logger, mock_objects_get, api_key_mutations):
        """Test revoking a key that does not exist or belong to the user."""
        info = fake_info()
        user = info.context.request.user
        non_existent_key_id = 999

        result = api_key_mutations.revoke_api_key(info, key_id=non_existent_key_id)

        mock_objects_get.assert_called_once_with(id=non_existent_key_id, user=user)

        mock_logger.warning.assert_called_once_with("API Key does not exist")

        assert isinstance(result, RevokeAPIKeyResult)
        assert result.ok is False
        assert result.code == "NOT_FOUND"
        assert result.message == "API key not found."
