"""Tests for AdminNode GraphQL node."""

from unittest.mock import MagicMock

from apps.mentorship.api.internal.nodes.admin import AdminNode


class TestAdminNode:
    """Tests for AdminNode fields."""

    def test_avatar_url_with_github_user(self):
        """Test avatar_url returns GitHub avatar URL when user exists."""
        node = MagicMock(spec=AdminNode)
        node.github_user = MagicMock(avatar_url="https://example.com/avatar.png")

        result = AdminNode.avatar_url(node)

        assert result == "https://example.com/avatar.png"

    def test_avatar_url_without_github_user(self):
        """Test avatar_url returns empty string when no GitHub user."""
        node = MagicMock(spec=AdminNode)
        node.github_user = None

        result = AdminNode.avatar_url(node)

        assert result == ""

    def test_login_with_github_user(self):
        """Test login returns GitHub login when user exists."""
        node = MagicMock(spec=AdminNode)
        node.github_user = MagicMock(login="admin-login")

        result = AdminNode.login(node)

        assert result == "admin-login"

    def test_login_without_github_user(self):
        """Test login returns empty string when no GitHub user."""
        node = MagicMock(spec=AdminNode)
        node.github_user = None

        result = AdminNode.login(node)

        assert result == ""

    def test_name_with_github_user(self):
        """Test name returns GitHub name when user exists."""
        node = MagicMock(spec=AdminNode)
        github_user = MagicMock()
        github_user.configure_mock(name="Admin User")
        node.github_user = github_user

        result = AdminNode.name(node)

        assert result == "Admin User"

    def test_name_without_github_user(self):
        """Test name returns empty string when no GitHub user."""
        node = MagicMock(spec=AdminNode)
        node.github_user = None

        result = AdminNode.name(node)

        assert result == ""
