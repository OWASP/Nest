from unittest.mock import MagicMock, patch

import pytest

from apps.nest.graphql.queries.api_key import APIKeyQueries


def fake_info():
    """Return fake information."""
    info = MagicMock()
    info.context = MagicMock()
    info.context.request = MagicMock()
    info.context.request.user = MagicMock()
    info.context.request.user.is_authenticated = True
    info.context.request.user.pk = 1
    return info


class TestAPIKeyQueries:
    """Test cases for the APIKeyQueries class."""

    @pytest.fixture
    def api_key_queries(self) -> APIKeyQueries:
        """Pytest fixture to return an instance of the query resolver class."""
        return APIKeyQueries()

    @patch("apps.nest.graphql.queries.api_key.APIKey.active_count_for_user")
    def test_active_api_key_count(self, mock_active_count, api_key_queries):
        """Tests the active_api_key_count resolver."""
        info = fake_info()
        user = info.context.request.user

        mock_active_count.return_value = 3
        result = api_key_queries.active_api_key_count(info)
        mock_active_count.assert_called_once_with(user)
        assert result == 3

    @patch("apps.nest.graphql.queries.api_key.APIKey.objects")
    def test_api_keys_default_excludes_revoked(self, mock_objects, api_key_queries):
        """Tests the api_keys resolver with its default behavior."""
        info = fake_info()
        user = info.context.request.user
        mock_active_keys_queryset = MagicMock()

        mock_objects.filter.return_value.order_by.return_value.filter.return_value = (
            mock_active_keys_queryset
        )
        result = api_key_queries.api_keys(info)
        mock_objects.filter.assert_called_once_with(user=user)
        mock_objects.filter.return_value.order_by.assert_called_once_with("-created_at")
        mock_objects.filter.return_value.order_by.return_value.filter.assert_called_once_with(
            is_revoked=False
        )
        assert result == mock_active_keys_queryset

    @patch("apps.nest.graphql.queries.api_key.APIKey.objects")
    def test_api_keys_includes_revoked(self, mock_objects, api_key_queries):
        """Tests the api_keys resolver."""
        info = fake_info()
        user = info.context.request.user
        mock_all_keys_queryset = MagicMock()

        mock_objects.filter.return_value.order_by.return_value.filter.return_value = (
            mock_all_keys_queryset
        )
        result = api_key_queries.api_keys(info, include_revoked=True)
        mock_objects.filter.assert_called_once_with(user=user)
        mock_objects.filter.return_value.order_by.assert_called_once_with("-created_at")
        mock_objects.filter.return_value.order_by.return_value.filter.assert_called_once_with(
            is_revoked=True
        )
        assert result == mock_all_keys_queryset
