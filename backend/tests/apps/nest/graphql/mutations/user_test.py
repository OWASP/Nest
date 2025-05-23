from unittest.mock import MagicMock, patch

import pytest

from apps.nest.graphql.mutations.user import GitHubAuth


@pytest.fixture
def mock_github_response():
    return {"data": {"viewer": {"id": "gh123", "login": "testuser"}}}


def test_github_auth_new_user(mock_github_response):
    """Test mutation without using the database"""
    with (
        patch("apps.nest.graphql.mutations.user.requests.post") as mock_post,
        patch("apps.nest.graphql.mutations.user.User.objects") as mock_objects,
    ):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value=mock_github_response),
            raise_for_status=MagicMock(),
        )

        mock_qs = MagicMock()
        mock_qs.first.return_value = None
        mock_objects.filter.return_value = mock_qs

        # Simulate user creation
        mock_user = MagicMock()
        mock_objects.create.return_value = mock_user

        result = GitHubAuth.mutate(None, MagicMock(), "valid_token")

        mock_post.assert_called_once()
        mock_objects.filter.assert_called_once_with(github_id="gh123")
        mock_objects.create.assert_called_once_with(github_id="gh123", username="testuser")
        assert result.auth_user == mock_user


def test_github_auth_existing_user(mock_github_response):
    """Test existing user flow without using the database"""
    with (
        patch("apps.nest.graphql.mutations.user.requests.post") as mock_post,
        patch("apps.nest.graphql.mutations.user.User.objects") as mock_objects,
    ):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value=mock_github_response),
            raise_for_status=MagicMock(),
        )

        mock_user = MagicMock()
        mock_qs = MagicMock()
        mock_qs.first.return_value = mock_user
        mock_objects.filter.return_value = mock_qs

        result = GitHubAuth.mutate(None, MagicMock(), "valid_token")

        mock_post.assert_called_once()
        mock_objects.filter.assert_called_once_with(github_id="gh123")
        mock_objects.create.assert_not_called()
        assert result.auth_user == mock_user
