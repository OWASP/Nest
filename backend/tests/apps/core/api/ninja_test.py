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

    @patch("apps.core.api.ninja.ApiKey.authenticate")
    def test_authenticate_success(self, mock_authenticate, api_key_auth):
        """Tests successful authentication with a valid API key."""
        raw_key = "valid_api_key_string"
        mock_request = MagicMock()
        mock_api_key_instance = MagicMock(spec=ApiKey)

        mock_authenticate.return_value = mock_api_key_instance

        result = api_key_auth.authenticate(mock_request, key=raw_key)

        mock_authenticate.assert_called_once_with(raw_key=raw_key)
        assert result == mock_api_key_instance

    @patch("apps.core.api.ninja.ApiKey.authenticate")
    def test_authenticate_failure_invalid_key(self, mock_authenticate, api_key_auth):
        """Tests authentication failure."""
        raw_key = "non_existent_or_invalid_key"
        mock_request = MagicMock()

        mock_authenticate.return_value = None

        with pytest.raises(HttpError) as exc_info:
            api_key_auth.authenticate(mock_request, key=raw_key)

        assert exc_info.value.status_code == 401
        assert str(exc_info.value.message) == "Invalid API key"

        mock_authenticate.assert_called_once_with(raw_key=raw_key)

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
