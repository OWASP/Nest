from unittest.mock import MagicMock, Mock, patch

import pytest
from django.db.models import Q

from apps.common.constants import MAX_SEARCH_QUERY_LENGTH, SEARCH_LIMIT
from apps.github.api.internal.nodes.user import USER_BADGES_PREFETCH
from apps.github.api.internal.queries.user import MAX_LIMIT, UserQuery
from apps.github.models.repository_contributor import RepositoryContributor
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
            mock_queryset.prefetch_related.return_value.first.return_value = mock_user

            result = UserQuery().user(login="test-user")

            assert result == mock_user
            mock_filter.assert_called_once_with(has_public_member_page=True, login="test-user")
            mock_queryset.prefetch_related.assert_called_once_with(USER_BADGES_PREFETCH)
            mock_queryset.prefetch_related.return_value.first.assert_called_once()

    def test_resolve_user_not_found_when_has_public_member_page_false(self):
        """Test resolving a user with has_public_member_page=False returns None."""
        with patch("apps.github.models.user.User.objects.filter") as mock_filter:
            mock_queryset = mock_filter.return_value
            mock_queryset.prefetch_related.return_value.first.return_value = None

            result = UserQuery().user(login="test-user")

            assert result is None
            mock_filter.assert_called_once_with(has_public_member_page=True, login="test-user")
            mock_queryset.prefetch_related.return_value.first.assert_called_once()

    def test_resolve_user_not_found(self):
        """Test resolving a non-existent user."""
        with patch("apps.github.models.user.User.objects.filter") as mock_filter:
            mock_queryset = mock_filter.return_value
            mock_queryset.prefetch_related.return_value.first.return_value = None

            result = UserQuery().user(login="non-existent")

            assert result is None
            mock_filter.assert_called_once_with(has_public_member_page=True, login="non-existent")
            mock_queryset.prefetch_related.return_value.first.assert_called_once()

    def test_resolve_user_filters_by_public_member_page_and_login(self):
        """Test that user query filters by both has_public_member_page and login."""
        with patch("apps.github.models.user.User.objects.filter") as mock_filter:
            mock_queryset = mock_filter.return_value
            mock_queryset.prefetch_related.return_value.first.return_value = None

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


class TestSearchUsers:
    """Test cases for UserQuery.search_users."""

    @pytest.mark.parametrize(
        "query",
        [
            "ab",
            "  ab  ",
            "a" * (MAX_SEARCH_QUERY_LENGTH + 1),
        ],
    )
    def test_search_users_invalid_query_length_returns_empty(self, query):
        """Test search_users returns [] for too-short or too-long queries."""
        with patch("apps.github.models.user.User.objects.filter") as mock_filter:
            result = UserQuery().search_users(query=query)

        assert result == []
        mock_filter.assert_not_called()

    def test_search_users_filters_and_slices(self):
        """Test search_users filters public members by login or name and limits results."""
        users = [Mock(spec=User), Mock(spec=User)]

        with patch("apps.github.models.user.User.objects.filter") as mock_filter:
            mock_ordered = MagicMock()
            mock_ordered.__getitem__.return_value = users
            mock_filter.return_value.order_by.return_value = mock_ordered

            result = UserQuery().search_users(query="  alice  ")

        assert result == users
        mock_filter.assert_called_once_with(
            Q(has_public_member_page=True),
            Q(login__icontains="alice") | Q(name__icontains="alice"),
        )
        mock_filter.return_value.order_by.assert_called_once_with("login")
        mock_ordered.__getitem__.assert_called_once_with(slice(None, SEARCH_LIMIT, None))


class TestEntityContributors:
    """Test cases for UserQuery.entity_contributors."""

    @pytest.fixture
    def mock_get_top_contributors(self):
        """Patch RepositoryContributor.get_top_contributors."""
        with patch.object(RepositoryContributor, "get_top_contributors") as mock_get_top:
            yield mock_get_top

    @pytest.fixture
    def mock_user_filter(self):
        """Patch User.objects.filter."""
        with patch("apps.github.models.user.User.objects.filter") as mock_filter:
            yield mock_filter

    @staticmethod
    def _make_user(login):
        user = Mock(spec=User)
        user.login = login
        return user

    def test_chapter_key_uses_top_contributors_for_chapter(
        self, mock_get_top_contributors, mock_user_filter
    ):
        """Test the chapter key is stripped of its prefix and passed as chapter."""
        user = self._make_user("alice")
        mock_get_top_contributors.return_value = [{"login": "alice"}]
        mock_user_filter.return_value.prefetch_related.return_value = [user]

        result = UserQuery().entity_contributors(chapter_key="  www-chapter-london  ")

        assert result == [user]
        mock_get_top_contributors.assert_called_once_with(
            chapter="london",
            limit=15,
            project=None,
        )
        mock_user_filter.assert_called_once_with(login__in=["alice"])
        mock_user_filter.return_value.prefetch_related.assert_called_once_with(
            USER_BADGES_PREFETCH
        )

    def test_project_key_uses_top_contributors_for_project(
        self, mock_get_top_contributors, mock_user_filter
    ):
        """Test the project key is stripped of its prefix and passed as project."""
        user = self._make_user("bob")
        mock_get_top_contributors.return_value = [{"login": "bob"}]
        mock_user_filter.return_value.prefetch_related.return_value = [user]

        result = UserQuery().entity_contributors(project_key="www-project-juice-shop", limit=5)

        assert result == [user]
        mock_get_top_contributors.assert_called_once_with(
            chapter=None,
            limit=5,
            project="juice-shop",
        )

    def test_order_preserved_and_missing_users_skipped(
        self, mock_get_top_contributors, mock_user_filter
    ):
        """Test users are returned in contributor order and unknown logins are skipped."""
        alice = self._make_user("alice")
        bob = self._make_user("bob")
        mock_get_top_contributors.return_value = [
            {"login": "bob"},
            {"login": "ghost"},
            {"login": "alice"},
        ]
        mock_user_filter.return_value.prefetch_related.return_value = [alice, bob]

        result = UserQuery().entity_contributors(project_key="juice-shop")

        assert result == [bob, alice]
        mock_user_filter.assert_called_once_with(login__in=["bob", "ghost", "alice"])

    def test_limit_is_capped(self, mock_get_top_contributors, mock_user_filter):
        """Test limits above MAX_LIMIT are capped."""
        mock_get_top_contributors.return_value = []
        mock_user_filter.return_value.prefetch_related.return_value = []

        result = UserQuery().entity_contributors(project_key="juice-shop", limit=MAX_LIMIT + 1)

        assert result == []
        mock_get_top_contributors.assert_called_once_with(
            chapter=None,
            limit=MAX_LIMIT,
            project="juice-shop",
        )

    @pytest.mark.parametrize(
        ("project_key", "chapter_key"),
        [
            (None, None),
            ("", ""),
            ("   ", "   "),
            ("www-project-", None),
            (None, "www-chapter-"),
        ],
    )
    def test_empty_keys_return_empty(
        self, mock_get_top_contributors, mock_user_filter, project_key, chapter_key
    ):
        """Test missing or blank keys return [] without querying."""
        result = UserQuery().entity_contributors(project_key=project_key, chapter_key=chapter_key)

        assert result == []
        mock_get_top_contributors.assert_not_called()
        mock_user_filter.assert_not_called()

    @pytest.mark.parametrize("limit", [0, -1])
    def test_invalid_limit_returns_empty(self, mock_get_top_contributors, mock_user_filter, limit):
        """Test a non-positive limit returns [] without querying."""
        result = UserQuery().entity_contributors(project_key="juice-shop", limit=limit)

        assert result == []
        mock_get_top_contributors.assert_not_called()
        mock_user_filter.assert_not_called()
