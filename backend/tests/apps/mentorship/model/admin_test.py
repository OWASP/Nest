"""Tests for Admin model."""

from unittest.mock import MagicMock

from apps.github.models import User as GithubUser
from apps.mentorship.models import Admin


class TestAdmin:
    """Tests for Admin model."""

    def test_str_returns_github_login(self):
        """Test __str__ returns the GitHub username."""
        github_user = MagicMock(spec=GithubUser, login="test_admin")

        admin = MagicMock(spec=Admin)
        admin.github_user = github_user

        assert Admin.__str__(admin) == "test_admin"
