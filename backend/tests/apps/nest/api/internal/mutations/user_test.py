"""Test cases for Nest user GraphQL Mutations."""

from unittest.mock import MagicMock, patch

import pytest
from github.AuthenticatedUser import AuthenticatedUser
from github.GithubException import BadCredentialsException

from apps.github.models.user import User as GitHubUser
from apps.nest.api.internal.mutations.user import GitHubAuthResult, UserMutations


def mock_info() -> MagicMock:
    """Return a minimal mock of strawberry `Info` with request on context."""
    info = MagicMock()
    info.context = MagicMock()
    info.context.request = MagicMock()
    return info


class TestGitHubAuthResult:
    """Test cases for GitHubAuthResult."""

    def test_github_auth_result_ok_true(self):
        result = GitHubAuthResult(ok=True, message="Success")
        assert result.ok
        assert result.message == "Success"

    def test_github_auth_result_ok_false(self):
        result = GitHubAuthResult(ok=False, message="Failed")
        assert not result.ok
        assert result.message == "Failed"


class TestUserMutations:
    """Test cases for UserMutations class."""

    @pytest.fixture
    def user_mutations(self):
        """Create UserMutations instance."""
        return UserMutations()

    @pytest.fixture
    def mock_github_user(self):
        """Mock GitHub user data."""
        mock_user = MagicMock()
        mock_user.id = 12345
        mock_user.login = "testuser"
        mock_user.email = "testuser@example.com"
        return mock_user

    def test_github_auth_new_user_success(self, user_mutations):
        """Test successful GitHub authentication for new user."""
        with (
            patch("apps.nest.api.internal.mutations.user.Github") as mock_github_class,
            patch("apps.nest.api.internal.mutations.user.User.objects") as mock_user_objects,
            patch(
                "apps.nest.api.internal.mutations.user.GithubUser.update_data"
            ) as mock_update_data,
            patch("apps.nest.api.internal.mutations.user.login"),
        ):
            info = mock_info()
            mock_github = MagicMock()
            mock_github_user = MagicMock(spec=AuthenticatedUser)
            mock_github_user.login = "test_user"
            mock_github_user.get_emails.return_value = [
                MagicMock(email="user@example.com", primary=True, verified=True)
            ]
            mock_github.get_user.return_value = mock_github_user
            mock_github_class.return_value = mock_github

            mock_github_user_model = MagicMock(spec=GitHubUser)
            mock_update_data.return_value = mock_github_user_model
            mock_user_objects.get_or_create.return_value = (MagicMock(), True)

            result = user_mutations.github_auth(info, "valid_token")
            assert isinstance(result, GitHubAuthResult)
            assert result.ok
            assert result.message == "Successfully authenticated with GitHub."

    def test_github_auth_no_primary_email(self, user_mutations):
        """Test GitHub auth fails if no primary verified email."""
        with (
            patch("apps.nest.api.internal.mutations.user.Github") as mock_github_class,
            patch("apps.nest.api.internal.mutations.user.login"),
        ):
            info = mock_info()
            mock_github = MagicMock()
            mock_github_user = MagicMock(spec=AuthenticatedUser)
            mock_github_user.login = "testuser"
            mock_github_user.get_emails.return_value = []
            mock_github.get_user.return_value = mock_github_user
            mock_github_class.return_value = mock_github

            result = user_mutations.github_auth(info, "token")
            assert not result.ok
            assert "Verified primary email" in result.message

    def test_github_auth_not_authenticated_user(self, user_mutations):
        """Test GitHub auth fails if user is not AuthenticatedUser."""
        with (
            patch("apps.nest.api.internal.mutations.user.Github") as mock_github_class,
            patch("apps.nest.api.internal.mutations.user.login"),
        ):
            info = mock_info()
            mock_github = MagicMock()
            mock_github_user = MagicMock()  # Not AuthenticatedUser
            mock_github_user.login = "testuser"
            mock_github.get_user.return_value = mock_github_user
            mock_github_class.return_value = mock_github

            result = user_mutations.github_auth(info, "token")
            assert not result.ok
            assert "Authenticated user required" in result.message

    def test_github_auth_update_data_returns_none(self, user_mutations):
        """Test GitHub auth fails when update_data returns None."""
        with (
            patch("apps.nest.api.internal.mutations.user.Github") as mock_github_class,
            patch(
                "apps.nest.api.internal.mutations.user.GithubUser.update_data"
            ) as mock_update_data,
            patch("apps.nest.api.internal.mutations.user.login"),
        ):
            info = mock_info()
            mock_github = MagicMock()
            mock_github_user = MagicMock(spec=AuthenticatedUser)
            mock_github_user.login = "testuser"
            mock_github_user.get_emails.return_value = [
                MagicMock(email="user@example.com", primary=True, verified=True)
            ]
            mock_github.get_user.return_value = mock_github_user
            mock_github_class.return_value = mock_github
            mock_update_data.return_value = None

            result = user_mutations.github_auth(info, "token")
            assert not result.ok
            assert "Failed to retrieve GitHub user" in result.message

    def test_github_auth_github_exception(self, user_mutations):
        """Test GitHub auth handles BadCredentialsException."""
        with patch("apps.nest.api.internal.mutations.user.Github") as mock_github_class:
            info = mock_info()
            mock_github = MagicMock()
            mock_github.get_user.side_effect = BadCredentialsException(401, "Unauthorized", None)
            mock_github_class.return_value = mock_github

            result = user_mutations.github_auth(info, "token")
            assert not result.ok
            assert "authentication request failed" in result.message.lower()
