"""Tests for mentorship utility functions."""

from unittest.mock import MagicMock

import pytest
import strawberry

from apps.github.models import User as GithubUser
from apps.mentorship.utils import has_program_access


@pytest.fixture
def mock_program() -> MagicMock:
    """Fixture for a mock Program instance."""
    return MagicMock()


@pytest.fixture
def mock_authenticated_info() -> MagicMock:
    """Fixture for a mock info with an authenticated user."""
    mock_github_user = MagicMock(spec=GithubUser, id=1, login="testuser")
    mock_user = MagicMock(id=1)
    mock_user.is_authenticated = True
    mock_user.github_user = mock_github_user
    mock_request = MagicMock()
    mock_request.user = mock_user
    mock_info = MagicMock(spec=strawberry.Info)
    mock_info.context.request = mock_request
    return mock_info


@pytest.fixture
def mock_anonymous_info() -> MagicMock:
    """Fixture for a mock info with an anonymous user."""
    mock_user = MagicMock(id=None)
    mock_user.is_authenticated = False
    mock_user.github_user = None
    mock_request = MagicMock()
    mock_request.user = mock_user
    mock_info = MagicMock(spec=strawberry.Info)
    mock_info.context.request = mock_request
    return mock_info


class TestHasProgramAccess:
    """Tests for has_program_access utility function."""

    def test_anonymous_user_has_no_access(
        self, mock_anonymous_info: MagicMock, mock_program: MagicMock
    ) -> None:
        """Test that anonymous users do not have access."""
        assert has_program_access(mock_anonymous_info, mock_program) is False

    def test_admin_has_access(
        self, mock_authenticated_info: MagicMock, mock_program: MagicMock
    ) -> None:
        """Test that a program admin has access."""
        mock_program.admins.filter.return_value.exists.return_value = True

        assert has_program_access(mock_authenticated_info, mock_program) is True

    def test_mentor_has_access(
        self, mock_authenticated_info: MagicMock, mock_program: MagicMock
    ) -> None:
        """Test that a mentor of the program has access."""
        mock_program.admins.filter.return_value.exists.return_value = False
        mock_program.modules.filter.return_value.exists.return_value = True

        assert has_program_access(mock_authenticated_info, mock_program) is True

    def test_authenticated_non_admin_non_mentor_has_no_access(
        self, mock_authenticated_info: MagicMock, mock_program: MagicMock
    ) -> None:
        """Test that an authenticated user who is not admin or mentor has no access."""
        mock_program.admins.filter.return_value.exists.return_value = False
        mock_program.modules.filter.return_value.exists.return_value = False

        assert has_program_access(mock_authenticated_info, mock_program) is False

    def test_authenticated_user_without_github_user(
        self, mock_program: MagicMock
    ) -> None:
        """Test that a user without a github_user who is not admin has no access."""
        mock_user = MagicMock(id=1)
        mock_user.is_authenticated = True
        mock_user.github_user = None
        mock_request = MagicMock()
        mock_request.user = mock_user
        mock_info = MagicMock(spec=strawberry.Info)
        mock_info.context.request = mock_request

        mock_program.admins.filter.return_value.exists.return_value = False

        assert has_program_access(mock_info, mock_program) is False
