"""Test cases for Nest API permissions."""

from unittest.mock import MagicMock

from graphql import GraphQLError

from apps.nest.api.internal.permissions import IsAuthenticated


class TestIsAuthenticated:
    """Test cases for IsAuthenticated permission class."""

    def test_has_permission_authenticated_user(self):
        """Test has_permission returns True for authenticated users."""
        permission = IsAuthenticated()
        info = MagicMock()
        info.context.request.user.is_authenticated = True

        assert permission.has_permission(None, info) is True

    def test_has_permission_unauthenticated_user(self):
        """Test has_permission returns False for unauthenticated users."""
        permission = IsAuthenticated()
        info = MagicMock()
        info.context.request.user.is_authenticated = False

        assert permission.has_permission(None, info) is False

    def test_on_unauthorized(self):
        """Test on_unauthorized returns GraphQLError."""
        permission = IsAuthenticated()
        
        result = permission.on_unauthorized()
        
        assert isinstance(result, GraphQLError)
        assert result.message == "You must be logged in to perform this action."
        assert result.extensions == {"code": "UNAUTHORIZED"}
