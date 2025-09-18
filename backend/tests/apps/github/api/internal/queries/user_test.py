from unittest.mock import Mock, patch

import pytest

from apps.github.api.internal.queries.user import UserQuery
from apps.github.models.user import User


class TestUserQuery:
    """Test cases for UserQuery class."""

    @pytest.fixture
    def mock_user(self):
        """User mock fixture."""
        return Mock(spec=User)

    def test_resolve_user_existing_with_public_member_page(self, mock_user):
        """Test resolving an existing user with has_public_member_page=True."""
        with patch("apps.github.models.user.User.objects.filter") as mock_filter:
            mock_queryset = mock_filter.return_value
            mock_queryset.first.return_value = mock_user

            result = UserQuery().user(login="test-user")

            assert result == mock_user
            mock_filter.assert_called_once_with(has_public_member_page=True, login="test-user")
            mock_queryset.first.assert_called_once()

    def test_resolve_user_not_found_when_has_public_member_page_false(self):
        """Test resolving a user with has_public_member_page=False returns None."""
        with patch("apps.github.models.user.User.objects.filter") as mock_filter:
            mock_queryset = mock_filter.return_value
            mock_queryset.first.return_value = None

            result = UserQuery().user(login="test-user")

            assert result is None
            mock_filter.assert_called_once_with(has_public_member_page=True, login="test-user")
            mock_queryset.first.assert_called_once()

    def test_resolve_user_not_found(self):
        """Test resolving a non-existent user."""
        with patch("apps.github.models.user.User.objects.filter") as mock_filter:
            mock_queryset = mock_filter.return_value
            mock_queryset.first.return_value = None

            result = UserQuery().user(login="non-existent")

            assert result is None
            mock_filter.assert_called_once_with(has_public_member_page=True, login="non-existent")
            mock_queryset.first.assert_called_once()

    def test_resolve_user_filters_by_public_member_page_and_login(self):
        """Test that user query filters by both has_public_member_page and login."""
        with patch("apps.github.models.user.User.objects.filter") as mock_filter:
            mock_queryset = mock_filter.return_value
            mock_queryset.first.return_value = None

            UserQuery().user(login="test-user")

            mock_filter.assert_called_once_with(has_public_member_page=True, login="test-user")

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
