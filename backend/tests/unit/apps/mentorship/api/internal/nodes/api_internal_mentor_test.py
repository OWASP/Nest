"""Tests for MentorNode GraphQL node."""

from unittest.mock import MagicMock

import pytest

from apps.mentorship.api.internal.nodes.mentor import MentorNode
from apps.mentorship.models.mentor import Mentor


class TestMentorNode:
    """Tests for MentorNode fields."""

    @pytest.mark.asyncio
    async def test_avatar_url_with_github_user(self):
        """Test avatar_url returns GitHub avatar URL when user exists."""
        root = MagicMock(spec=Mentor)
        root.github_user = MagicMock(avatar_url="https://example.com/avatar.png")

        result = await MentorNode.avatar_url(MagicMock(spec=MentorNode), root)

        assert result == "https://example.com/avatar.png"

    @pytest.mark.asyncio
    async def test_avatar_url_without_github_user(self):
        """Test avatar_url returns empty string when no GitHub user."""
        root = MagicMock(spec=Mentor)
        root.github_user = None

        result = await MentorNode.avatar_url(MagicMock(spec=MentorNode), root)

        assert result == ""

    @pytest.mark.asyncio
    async def test_name_with_github_user(self):
        """Test name returns GitHub name when user exists."""
        root = MagicMock(spec=Mentor)
        github_user = MagicMock()
        github_user.configure_mock(name="Mentor Name")
        root.github_user = github_user

        result = await MentorNode.name(MagicMock(spec=MentorNode), root)

        assert result == "Mentor Name"

    @pytest.mark.asyncio
    async def test_name_without_github_user(self):
        """Test name returns empty string when no GitHub user."""
        root = MagicMock(spec=Mentor)
        root.github_user = None

        result = await MentorNode.name(MagicMock(spec=MentorNode), root)

        assert result == ""

    @pytest.mark.asyncio
    async def test_login_with_github_user(self):
        """Test login returns GitHub login when user exists."""
        root = MagicMock(spec=Mentor)
        root.github_user = MagicMock(login="mentor-login")

        result = await MentorNode.login(MagicMock(spec=MentorNode), root)

        assert result == "mentor-login"

    @pytest.mark.asyncio
    async def test_login_without_github_user(self):
        """Test login returns empty string when no GitHub user."""
        root = MagicMock(spec=Mentor)
        root.github_user = None

        result = await MentorNode.login(MagicMock(spec=MentorNode), root)

        assert result == ""

    def test_mentor_node_id(self):
        """Test that MentorNode id is correctly assigned."""
        node = MentorNode(id="1")
        assert str(node.id) == "1"
