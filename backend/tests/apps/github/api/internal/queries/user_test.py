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

    @patch("apps.github.models.user.User.objects.filter")
    @patch("apps.github.models.user.User.objects.select_related")
    def test_resolve_user_found_on_first_query(self, mock_select_related, mock_filter, mock_user):
        """Test resolving an existing user on the first query."""
        mock_select_related.return_value.filter.return_value.first.return_value = mock_user

        result = UserQuery().user(login="test-user")

        assert result == mock_user
        mock_select_related.assert_called_once_with("owasp_profile")
        mock_select_related.return_value.filter.assert_called_once_with(
            owasp_profile__has_public_member_page=True, login="test-user"
        )
        mock_filter.assert_not_called()

    @patch("apps.github.models.user.User.objects.filter")
    @patch("apps.github.models.user.User.objects.select_related")
    def test_resolve_user_found_on_second_query(self, mock_select_related, mock_filter, mock_user):
        """Test resolving an existing user on the second (fallback) query."""
        mock_select_related.return_value.filter.return_value.first.return_value = None
        mock_filter.return_value.first.return_value = mock_user

        result = UserQuery().user(login="test-user")

        assert result == mock_user
        mock_select_related.assert_called_once_with("owasp_profile")
        mock_select_related.return_value.filter.assert_called_once_with(
            owasp_profile__has_public_member_page=True, login="test-user"
        )
        mock_filter.assert_called_once_with(has_public_member_page=True, login="test-user")

    @patch("apps.github.models.user.User.objects.filter")
    @patch("apps.github.models.user.User.objects.select_related")
    def test_resolve_user_not_found(self, mock_select_related, mock_filter):
        """Test resolving a non-existent user returns None."""
        mock_select_related.return_value.filter.return_value.first.return_value = None
        mock_filter.return_value.first.return_value = None

        result = UserQuery().user(login="non-existent")

        assert result is None
        mock_select_related.assert_called_once_with("owasp_profile")
        mock_select_related.return_value.filter.assert_called_once_with(
            owasp_profile__has_public_member_page=True, login="non-existent"
        )
        mock_filter.assert_called_once_with(has_public_member_page=True, login="non-existent")

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
