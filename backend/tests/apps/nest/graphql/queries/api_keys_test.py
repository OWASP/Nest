from unittest.mock import MagicMock, patch

import pytest

from apps.nest.graphql.queries.api_key import ApiKeyQueries


def fake_info():
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
        info = fake_info()
        user = info.context.request.user

        user.active_api_keys.count.return_value = 3

        result = api_key_queries.active_api_key_count(info)

        user.active_api_keys.count.assert_called_once()
        assert result == 3

    @patch("apps.nest.graphql.queries.api_key.ApiKey.objects")
    def test_api_keys_resolver(self, mock_objects, api_key_queries):
        """Tests the api_keys resolver with its default behavior."""
        info = fake_info()
        user = info.context.request.user
        mock_active_keys_queryset = MagicMock()

        mock_objects.filter.return_value.order_by.return_value = mock_active_keys_queryset
        result = api_key_queries.api_keys(info)

        mock_objects.filter.assert_called_once_with(user=user, is_revoked=False)
        mock_objects.filter.return_value.order_by.assert_called_once_with("-created_at")

        assert result == mock_active_keys_queryset
