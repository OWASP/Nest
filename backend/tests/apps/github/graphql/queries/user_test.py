from unittest.mock import Mock, patch

import pytest

from apps.github.graphql.queries.user import UserQuery
from apps.github.models.user import User


class TestUserQuery:
    """Test cases for UserQuery class."""

    @pytest.fixture
    def mock_user(self):
        """User mock fixture."""
        return Mock(spec=User)

    def test_resolve_user_existing(self, mock_user):
        """Test resolving an existing user."""
        with patch("apps.github.models.user.User.objects.get") as mock_get:
            mock_get.return_value = mock_user

            result = UserQuery().user(login="test-user")

            assert result == mock_user
            mock_get.assert_called_once_with(login="test-user")

    def test_resolve_user_not_found(self):
        """Test resolving a non-existent user."""
        with patch("apps.github.models.user.User.objects.get") as mock_get:
            mock_get.side_effect = User.DoesNotExist

            result = UserQuery().user(login="non-existent")

            assert result is None
            mock_get.assert_called_once_with(login="non-existent")

    def test_top_contributed_repositories(self):
        """Test resolving top contributed repositories."""
        mock_repository = Mock()
        mock_contributor = Mock(repository=mock_repository)

        with patch(
            "apps.github.models.repository_contributor.RepositoryContributor.objects.select_related"
        ) as mock_select_related:
            mock_queryset = mock_select_related.return_value
            mock_queryset.filter.return_value.order_by.return_value = [mock_contributor]

            result = UserQuery().top_contributed_repositories(login="test-user")

            assert result == [mock_repository]
            mock_select_related.assert_called_once_with("repository", "repository__organization")
            mock_queryset.filter.assert_called_once_with(user__login="test-user")
            mock_queryset.filter.return_value.order_by.assert_called_once_with(
                "-contributions_count"
            )
