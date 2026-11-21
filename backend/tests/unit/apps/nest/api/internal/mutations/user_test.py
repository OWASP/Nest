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
            mock_user_objects.filter.return_value.first.return_value = None
            mock_user_objects.get_or_create.return_value = (MagicMock(), True)

            result = user_mutations.github_auth(info, "valid_token")
            assert isinstance(result, GitHubAuthResult)
            assert result.ok
            assert result.message == "Successfully authenticated with GitHub."

    def test_github_auth_links_existing_user(self, user_mutations):
        """Test GitHub authentication links an existing unlinked Nest user."""
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
            mock_github_user.login = "existing_user"
            mock_github_user.get_emails.return_value = [
                MagicMock(email="user@example.com", primary=True, verified=True)
            ]
            mock_github.get_user.return_value = mock_github_user
            mock_github_class.return_value = mock_github

            github_user = MagicMock(spec=GitHubUser)
            nest_user = MagicMock()
            nest_user.github_user_id = None
            mock_update_data.return_value = github_user
            mock_user_objects.filter.return_value.first.return_value = None
            mock_user_objects.get_or_create.return_value = (nest_user, False)

            result = user_mutations.github_auth(info, "valid_token")

            assert result.ok
            assert nest_user.github_user is github_user
            nest_user.save.assert_called_once_with(update_fields=["github_user"])

    def test_github_auth_rejects_different_existing_link(self, user_mutations):
        """Test GitHub authentication rejects a username with another GitHub link."""
        with (
            patch("apps.nest.api.internal.mutations.user.Github") as mock_github_class,
            patch("apps.nest.api.internal.mutations.user.User.objects") as mock_user_objects,
            patch(
                "apps.nest.api.internal.mutations.user.GithubUser.update_data"
            ) as mock_update_data,
            patch("apps.nest.api.internal.mutations.user.login") as mock_login,
        ):
            info = mock_info()
            mock_github = MagicMock()
            mock_github_user = MagicMock(spec=AuthenticatedUser)
            mock_github_user.login = "existing_user"
            mock_github_user.get_emails.return_value = [
                MagicMock(email="user@example.com", primary=True, verified=True)
            ]
            mock_github.get_user.return_value = mock_github_user
            mock_github_class.return_value = mock_github

            github_user = MagicMock(spec=GitHubUser)
            existing_link = MagicMock(spec=GitHubUser)
            nest_user = MagicMock()
            nest_user.github_user_id = existing_link.id = 123
            nest_user.github_user = existing_link
            mock_update_data.return_value = github_user
            mock_user_objects.filter.return_value.first.return_value = None
            mock_user_objects.get_or_create.return_value = (nest_user, False)

            result = user_mutations.github_auth(info, "valid_token")

            assert not result.ok
            assert "different GitHub account" in result.message
            assert nest_user.github_user is existing_link
            nest_user.save.assert_not_called()
            mock_login.assert_not_called()

    def test_github_auth_uses_existing_github_link(self, user_mutations):
        """Test GitHub authentication uses the user already linked to the identity."""
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
            mock_github_user.login = "username-conflict"
            mock_github_user.get_emails.return_value = [
                MagicMock(email="user@example.com", primary=True, verified=True)
            ]
            mock_github.get_user.return_value = mock_github_user
            mock_github_class.return_value = mock_github

            github_user = MagicMock(spec=GitHubUser)
            linked_user = MagicMock()
            linked_user.github_user_id = github_user.id = 123
            mock_update_data.return_value = github_user
            mock_user_objects.filter.return_value.first.return_value = linked_user

            result = user_mutations.github_auth(info, "valid_token")

            assert result.ok
            assert result.user is linked_user
            mock_user_objects.get_or_create.assert_not_called()

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

    def test_logout_user_not_authenticated(self, user_mutations):
        """Test logout when user is not authenticated."""
        info = mock_info()
        info.context.request.user.is_authenticated = False

        result = user_mutations.logout_user(info)
        assert not result.ok
        assert result.message == "User is not logged in."

    def test_logout_user_success(self, user_mutations):
        """Test successful user logout."""
        with patch("apps.nest.api.internal.mutations.user.logout") as mock_logout:
            info = mock_info()
            info.context.request.user.is_authenticated = True

            result = user_mutations.logout_user(info)
            assert result.ok
            assert result.message == "User logged out successfully."
            mock_logout.assert_called_once_with(info.context.request)
