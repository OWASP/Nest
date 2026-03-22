"""Tests for mentorship utility functions."""

from unittest.mock import MagicMock

from apps.github.models import User as GithubUser
from apps.mentorship.models.program import Program


class TestUserHasAccess:
    """Tests for Program.user_has_access method."""

    def test_anonymous_user_has_no_access(self) -> None:
        """Test that anonymous users do not have access."""
        mock_user = MagicMock()
        mock_user.is_authenticated = False

        program = MagicMock(spec=Program)

        assert Program.user_has_access(program, mock_user) is False

    def test_admin_has_access(self) -> None:
        """Test that a program admin has access."""
        mock_user = MagicMock()
        mock_user.is_authenticated = True

        program = MagicMock(spec=Program)
        program.admins.filter.return_value.exists.return_value = True

        assert Program.user_has_access(program, mock_user) is True

    def test_mentor_has_access(self) -> None:
        """Test that a mentor of the program has access."""
        mock_github_user = MagicMock(spec=GithubUser, id=1, login="testuser")
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.github_user = mock_github_user

        program = MagicMock(spec=Program)
        program.admins.filter.return_value.exists.return_value = False
        program.modules.filter.return_value.exists.return_value = True

        assert Program.user_has_access(program, mock_user) is True

    def test_authenticated_non_admin_non_mentor_has_no_access(self) -> None:
        """Test that an authenticated user who is not admin or mentor has no access."""
        mock_github_user = MagicMock(spec=GithubUser, id=1, login="testuser")
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.github_user = mock_github_user

        program = MagicMock(spec=Program)
        program.admins.filter.return_value.exists.return_value = False
        program.modules.filter.return_value.exists.return_value = False

        assert Program.user_has_access(program, mock_user) is False

    def test_authenticated_user_without_github_user(self) -> None:
        """Test that a user without a github_user who is not admin has no access."""
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.github_user = None

        program = MagicMock(spec=Program)
        program.admins.filter.return_value.exists.return_value = False

        assert Program.user_has_access(program, mock_user) is False
