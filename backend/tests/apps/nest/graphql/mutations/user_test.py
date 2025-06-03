"""Test cases for Nest user GraphQL Mutations."""

from unittest.mock import MagicMock, patch

import pytest

from apps.github.models import User as GitHubUser
from apps.nest.graphql.mutations.user import GitHubAuthResult, UserMutations
from apps.nest.models import User


class TestGitHubAuthResult:
    """Test cases for GitHubAuthResult."""

    def test_github_auth_result_with_user(self):
        """Test GitHubAuthResult with valid user."""
        mock_user = MagicMock()
        result = GitHubAuthResult(auth_user=mock_user)
        assert result.auth_user == mock_user

    def test_github_auth_result_without_user(self):
        """Test GitHubAuthResult with None user."""
        result = GitHubAuthResult(auth_user=None)
        assert result.auth_user is None


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

    @pytest.fixture
    def mock_info(self):
        """Mock GraphQL info object."""
        return MagicMock()

    def test_github_auth_new_user_success(self, user_mutations, mock_info, mock_github_user):
        """Test successful GitHub authentication for new user."""
        with (
            patch("apps.nest.graphql.mutations.user.Github") as mock_github_class,
            patch("apps.nest.graphql.mutations.user.User.objects") as mock_user_objects,
            patch("apps.nest.graphql.mutations.user.GithubUser.update_data") as mock_update_data,
        ):
            mock_github = MagicMock()
            mock_github.get_user.return_value = mock_github_user
            mock_github_class.return_value = mock_github

            # GitHubUser.update_data returns mocked GitHubUser
            mock_github_user_model = MagicMock(spec=GitHubUser)
            mock_update_data.return_value = mock_github_user_model

            # Simulate User.objects.get -> DoesNotExist
            mock_user_objects.get.side_effect = User.DoesNotExist

            # Simulate user creation
            mock_created_user = MagicMock()
            mock_user_objects.create.return_value = mock_created_user

            result = user_mutations.github_auth(mock_info, "valid_token")

            mock_update_data.assert_called_once_with(mock_github_user)
            mock_user_objects.create.assert_called_once_with(
                github_id="12345",
                github_user=mock_github_user_model,
                username="testuser",
            )
            assert isinstance(result, GitHubAuthResult)
            assert result.auth_user == mock_created_user

    def test_github_auth_update_data_returns_none(
        self, user_mutations, mock_info, mock_github_user
    ):
        """Test GitHub auth fails when update_data returns None."""
        with (
            patch("apps.nest.graphql.mutations.user.Github") as mock_github_class,
            patch("apps.nest.graphql.mutations.user.GithubUser.update_data") as mock_update_data,
        ):
            mock_github = MagicMock()
            mock_github.get_user.return_value = mock_github_user
            mock_github_class.return_value = mock_github

            mock_update_data.return_value = None

            result = user_mutations.github_auth(mock_info, "token")
            assert result.auth_user is None
