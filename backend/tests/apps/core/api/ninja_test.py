from unittest.mock import MagicMock, patch

import pytest
from ninja.errors import HttpError

from apps.core.api.ninja import ApiKeyAuth
from apps.nest.models import ApiKey


class TestApiKeyAuth:
    """Test cases for the ApiKeyAuth class."""

    @pytest.fixture
    def api_key_auth(self) -> ApiKeyAuth:
        """Pytest fixture to provide an instance of the ApiKeyAuth class."""
        return ApiKeyAuth()

    def test_param_name_configuration(self, api_key_auth):
        """Tests that the header parameter name is correctly configured."""
        assert api_key_auth.param_name == "X-API-Key"

    @patch("apps.core.api.ninja.ApiKey.objects.get")
    @patch("apps.core.api.ninja.ApiKey.generate_hash_key")
    def test_authenticate_success(self, mock_generate_hash, mock_objects_get, api_key_auth):
        """Tests successful authentication with a valid API key."""
        raw_key = "valid_api_key_string"
        hashed_key = "hashed_representation_of_the_key"
        mock_request = MagicMock()

        mock_api_key_instance = MagicMock(spec=ApiKey)
        mock_api_key_instance.is_valid.return_value = True

        mock_generate_hash.return_value = hashed_key
        mock_objects_get.return_value = mock_api_key_instance

        result = api_key_auth.authenticate(mock_request, key=raw_key)

        mock_generate_hash.assert_called_once_with(raw_key)
        mock_objects_get.assert_called_once_with(hash=hashed_key)
        mock_api_key_instance.is_valid.assert_called_once()
        assert result == mock_api_key_instance

    @patch("apps.core.api.ninja.ApiKey.objects.get")
    @patch("apps.core.api.ninja.ApiKey.generate_hash_key")
    def test_authenticate_failure_key_not_found(
        self, mock_generate_hash, mock_objects_get, api_key_auth
    ):
        """Tests authentication failure when the API key does not exist in the database."""
        raw_key = "non_existent_key"
        mock_request = MagicMock()

        mock_objects_get.side_effect = ApiKey.DoesNotExist

        with pytest.raises(HttpError) as exc_info:
            api_key_auth.authenticate(mock_request, key=raw_key)

        assert exc_info.value.status_code == 401
        assert str(exc_info.value.message) == "Invalid API key"

        mock_generate_hash.assert_called_once_with(raw_key)
        mock_objects_get.assert_called_once()

    @patch("apps.core.api.ninja.ApiKey.objects.get")
    @patch("apps.core.api.ninja.ApiKey.generate_hash_key")
    def test_authenticate_failure_key_is_invalid(
        self, mock_generate_hash, mock_objects_get, api_key_auth
    ):
        """Tests authentication failure when the API key exists but is invalid."""
        raw_key = "revoked_or_expired_key"
        mock_request = MagicMock()

        mock_api_key_instance = MagicMock(spec=ApiKey)
        mock_api_key_instance.is_valid.return_value = False

        mock_objects_get.return_value = mock_api_key_instance

        with pytest.raises(HttpError) as exc_info:
            api_key_auth.authenticate(mock_request, key=raw_key)

        assert exc_info.value.status_code == 401
        assert str(exc_info.value.message) == "Invalid API key"

        mock_api_key_instance.is_valid.assert_called_once()

    def test_authenticate_failure_key_is_missing(self, api_key_auth):
        """Tests authentication failure when the key is None or an empty string."""
        mock_request = MagicMock()

        with pytest.raises(HttpError) as exc_info_empty:
            api_key_auth.authenticate(mock_request, key="")

        assert exc_info_empty.value.status_code == 401
        assert str(exc_info_empty.value.message) == "Missing API key in 'X-API-Key' header"

        with pytest.raises(HttpError) as exc_info_none:
            api_key_auth.authenticate(mock_request, key=None)

        assert exc_info_none.value.status_code == 401
        assert str(exc_info_none.value.message) == "Missing API key in 'X-API-Key' header"
