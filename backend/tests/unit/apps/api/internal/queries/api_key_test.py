from unittest.mock import MagicMock

import pytest

from apps.api.internal.queries.api_key import ApiKeyQueries


def mock_info():
    """Return fake information with a mocked user object."""
    info = MagicMock()
    info.context = MagicMock()
    info.context.request = MagicMock()
    info.context.request.user = MagicMock()
    info.context.request.user.is_authenticated = True
    info.context.request.user.pk = 1
    return info


class TestApiKeyQueries:
    """Test cases for the ApiKeyQueries class."""

    @pytest.fixture
    def api_key_queries(self) -> ApiKeyQueries:
        """Pytest fixture to return an instance of the query resolver class."""
        return ApiKeyQueries()

    def test_active_api_key_count(self, api_key_queries):
        """Tests the active_api_key_count resolver using the user property."""
        info = mock_info()
        user = info.context.request.user

        user.active_api_keys.count.return_value = 3

        result = api_key_queries.active_api_key_count(info)

        user.active_api_keys.count.assert_called_once()
        assert result == 3

    def test_api_keys_resolver(self, api_key_queries):
        """Tests the api_keys resolver with its default behavior."""
        info = mock_info()
        qs = MagicMock(name="qs")
        info.context.request.user.active_api_keys.order_by.return_value = qs
        result = api_key_queries.api_keys(info)

        info.context.request.user.active_api_keys.order_by.assert_called_once_with("-created_at")
        assert result is qs
