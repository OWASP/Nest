"""Tests for AdminNode GraphQL node."""

from unittest.mock import MagicMock

import pytest

from apps.mentorship.api.internal.nodes.admin import AdminNode
from apps.mentorship.models.admin import Admin


class TestAdminNode:
    """Tests for AdminNode fields."""

    @pytest.mark.asyncio
    async def test_avatar_url_with_github_user(self):
        """Test avatar_url returns GitHub avatar URL when user exists."""
        root = MagicMock(spec=Admin)
        root.github_user = MagicMock(avatar_url="https://example.com/avatar.png")

        result = await AdminNode.avatar_url(MagicMock(spec=AdminNode), root)

        assert result == "https://example.com/avatar.png"

    @pytest.mark.asyncio
    async def test_avatar_url_without_github_user(self):
        """Test avatar_url returns empty string when no GitHub user."""
        root = MagicMock(spec=Admin)
        root.github_user = None

        result = await AdminNode.avatar_url(MagicMock(spec=AdminNode), root)

        assert result == ""

    @pytest.mark.asyncio
    async def test_login_with_github_user(self):
        """Test login returns GitHub login when user exists."""
        root = MagicMock(spec=Admin)
        root.github_user = MagicMock(login="admin-login")

        result = await AdminNode.login(MagicMock(spec=AdminNode), root)

        assert result == "admin-login"

    @pytest.mark.asyncio
    async def test_login_without_github_user(self):
        """Test login returns empty string when no GitHub user."""
        root = MagicMock(spec=Admin)
        root.github_user = None

        result = await AdminNode.login(MagicMock(spec=AdminNode), root)

        assert result == ""

    @pytest.mark.asyncio
    async def test_name_with_github_user(self):
        """Test name returns GitHub name when user exists."""
        root = MagicMock(spec=Admin)
        github_user = MagicMock()
        github_user.configure_mock(name="Admin User")
        root.github_user = github_user

        result = await AdminNode.name(MagicMock(spec=AdminNode), root)

        assert result == "Admin User"

    @pytest.mark.asyncio
    async def test_name_without_github_user(self):
        """Test name returns empty string when no GitHub user."""
        root = MagicMock(spec=Admin)
        root.github_user = None

        result = await AdminNode.name(MagicMock(spec=AdminNode), root)

        assert result == ""
