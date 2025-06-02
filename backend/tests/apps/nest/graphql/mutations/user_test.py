"""Test cases for Nest user GraphQL Mutations."""

from unittest.mock import MagicMock, patch

import pytest

from apps.nest.graphql.mutations.user import GitHubAuthResult, UserMutations


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
        ):
            # Setup mocks
            mock_github = MagicMock()
            mock_github.get_user.return_value = mock_github_user
            mock_github_class.return_value = mock_github

            # Mock user query - no existing user
            mock_qs = MagicMock()
            mock_qs.first.return_value = None
            mock_user_objects.filter.return_value = mock_qs

            # Mock user creation
            mock_created_user = MagicMock()
            mock_created_user.github_id = 12345
            mock_created_user.username = "testuser"
            mock_created_user.email = "testuser@example.com"
            mock_user_objects.create.return_value = mock_created_user

            # Execute mutation
            result = user_mutations.github_auth(mock_info, "valid_access_token")

            # Assertions
            mock_github_class.assert_called_once_with("valid_access_token")
            mock_github.get_user.assert_called_once()
            mock_user_objects.filter.assert_called_once_with(github_id=12345)
            mock_user_objects.create.assert_called_once_with(
                github_id=12345, username="testuser", email="testuser@example.com"
            )
            assert isinstance(result, GitHubAuthResult)
            assert result.auth_user == mock_created_user

    def test_github_auth_existing_user_success(self, user_mutations, mock_info, mock_github_user):
        """Test successful GitHub authentication for existing user."""
        with (
            patch("apps.nest.graphql.mutations.user.Github") as mock_github_class,
            patch("apps.nest.graphql.mutations.user.User.objects") as mock_user_objects,
        ):
            # Setup mocks
            mock_github = MagicMock()
            mock_github.get_user.return_value = mock_github_user
            mock_github_class.return_value = mock_github

            # Mock existing user
            mock_existing_user = MagicMock()
            mock_existing_user.github_id = 12345
            mock_existing_user.username = "testuser"
            mock_existing_user.email = "testuser@example.com"

            mock_qs = MagicMock()
            mock_qs.first.return_value = mock_existing_user
            mock_user_objects.filter.return_value = mock_qs

            # Execute mutation
            result = user_mutations.github_auth(mock_info, "valid_access_token")

            # Assertions
            mock_github_class.assert_called_once_with("valid_access_token")
            mock_github.get_user.assert_called_once()
            mock_user_objects.filter.assert_called_once_with(github_id=12345)
            mock_user_objects.create.assert_not_called()
            assert isinstance(result, GitHubAuthResult)
            assert result.auth_user == mock_existing_user
