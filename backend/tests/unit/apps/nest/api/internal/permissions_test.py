"""Test cases for Nest API permissions."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from graphql import GraphQLError

from apps.nest.api.internal.permissions import IsAuthenticated, IsAuthenticatedAsync


class TestIsAuthenticated:
    """Test cases for IsAuthenticated permission class."""

    def test_has_permission_authenticated_user(self):
        """Test has_permission returns True for authenticated users."""
        permission = IsAuthenticated()
        info = MagicMock()
        info.context.request.user.is_authenticated = True

        assert permission.has_permission(None, info)

    def test_has_permission_unauthenticated_user(self):
        """Test has_permission returns False for unauthenticated users."""
        permission = IsAuthenticated()
        info = MagicMock()
        info.context.request.user.is_authenticated = False

        assert not permission.has_permission(None, info)

    def test_on_unauthorized(self):
        """Test on_unauthorized returns GraphQLError."""
        permission = IsAuthenticated()

        result = permission.on_unauthorized()

        assert isinstance(result, GraphQLError)
        assert result.message == "You must be logged in to perform this action."
        assert result.extensions == {"code": "UNAUTHORIZED"}


class TestIsAuthenticatedAsync:
    """Test cases for IsAuthenticatedAsync permission class."""

    @pytest.mark.asyncio
    async def test_has_permission_authenticated_user(self):
        """Test has_permission returns True for authenticated users."""
        permission = IsAuthenticatedAsync()
        info = MagicMock()
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        info.context.request.auser = AsyncMock(return_value=mock_user)

        result = await permission.has_permission(None, info)

        assert result is True
        info.context.request.auser.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_has_permission_unauthenticated_user(self):
        """Test has_permission returns False for unauthenticated users."""
        permission = IsAuthenticatedAsync()
        info = MagicMock()
        mock_user = MagicMock()
        mock_user.is_authenticated = False
        info.context.request.auser = AsyncMock(return_value=mock_user)

        result = await permission.has_permission(None, info)

        assert result is False
        info.context.request.auser.assert_awaited_once()

    def test_on_unauthorized(self):
        """Test on_unauthorized returns GraphQLError with UNAUTHORIZED code."""
        permission = IsAuthenticatedAsync()

        result = permission.on_unauthorized()

        assert isinstance(result, GraphQLError)
        assert result.message == "You must be logged in to perform this action."
        assert result.extensions == {"code": "UNAUTHORIZED"}
