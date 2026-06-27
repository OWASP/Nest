"""Tests for user dataloaders."""

from unittest.mock import MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.user import (
    USER_BADGES_BY_USER_ID_LOADER,
    USER_ISSUES_COUNT_LOADER,
    USER_RELEASES_COUNT_LOADER,
    get_user_loaders,
    load_user_badges_by_user_id,
    load_user_issues_count,
    load_user_releases_count,
)


class TestLoadUserBadgesByUserId:
    """Tests for load_user_badges_by_user_id."""

    @patch("apps.github.api.internal.dataloaders.user.UserBadge")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_user_badge):
        """Queryset uses filter, select_related, and order_by."""
        mock_qs = MagicMock()
        mock_user_badge.objects.select_related.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.order_by.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter([])

        await load_user_badges_by_user_id([1, 2])

        mock_user_badge.objects.select_related.assert_called_once_with("badge")
        mock_qs.filter.assert_called_once_with(user_id__in=[1, 2], is_active=True)
        mock_qs.order_by.assert_called_once_with("badge__weight", "badge__name")

    @patch("apps.github.api.internal.dataloaders.user.UserBadge")
    @pytest.mark.asyncio
    async def test_returns_badges_grouped_by_user_id(self, mock_user_badge):
        """Badges are grouped by user ID in the correct order."""
        badge_1 = MagicMock()
        badge_2 = MagicMock()
        badge_3 = MagicMock()

        user_badges = [
            MagicMock(user_id=1, badge=badge_1),
            MagicMock(user_id=1, badge=badge_2),
            MagicMock(user_id=2, badge=badge_3),
        ]

        mock_qs = mock_user_badge.objects.select_related.return_value
        mock_qs.filter.return_value = mock_qs
        mock_qs.order_by.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter(user_badges)

        result = await load_user_badges_by_user_id([1, 2])

        assert result == [[badge_1, badge_2], [badge_3]]

    @patch("apps.github.api.internal.dataloaders.user.UserBadge")
    @pytest.mark.asyncio
    async def test_empty_user_ids(self, mock_user_badge):
        """An empty user_ids list returns an empty list."""
        mock_qs = mock_user_badge.objects.select_related.return_value
        mock_qs.filter.return_value = mock_qs
        mock_qs.order_by.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter([])

        result = await load_user_badges_by_user_id([])

        assert result == []

    @patch("apps.github.api.internal.dataloaders.user.UserBadge")
    @pytest.mark.asyncio
    async def test_user_with_no_badges_returns_empty_list(self, mock_user_badge):
        """A user with no badges yields an empty list."""
        mock_qs = mock_user_badge.objects.select_related.return_value
        mock_qs.filter.return_value = mock_qs
        mock_qs.order_by.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter([])

        result = await load_user_badges_by_user_id([1])

        assert result == [[]]

    @patch("apps.github.api.internal.dataloaders.user.UserBadge")
    @pytest.mark.asyncio
    async def test_order_matches_keys_not_queryset(self, mock_user_badge):
        """The output order follows user_ids, not the queryset iteration order."""
        badge_a = MagicMock()
        badge_b = MagicMock()

        user_badges = [
            MagicMock(user_id=2, badge=badge_a),
            MagicMock(user_id=1, badge=badge_b),
        ]

        mock_qs = mock_user_badge.objects.select_related.return_value
        mock_qs.filter.return_value = mock_qs
        mock_qs.order_by.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter(user_badges)

        result = await load_user_badges_by_user_id([1, 2])

        assert result == [[badge_b], [badge_a]]


class TestLoadUserIssuesCount:
    """Tests for load_user_issues_count."""

    @patch("apps.github.api.internal.dataloaders.user.User")
    @pytest.mark.asyncio
    async def test_returns_counts_grouped_by_user_id(self, mock_user):
        """Issues counts are grouped by user ID in the correct order."""
        users_data = [
            MagicMock(pk=1, items_count=5),
            MagicMock(pk=2, items_count=3),
        ]
        mock_qs = MagicMock()
        mock_user.objects.filter.return_value = mock_qs
        mock_qs.annotate.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter(users_data)

        result = await load_user_issues_count([1, 2])

        assert result == [5, 3]

    @patch("apps.github.api.internal.dataloaders.user.User")
    @pytest.mark.asyncio
    async def test_empty_user_ids(self, mock_user):
        """An empty user_ids list returns an empty list."""
        mock_qs = MagicMock()
        mock_user.objects.filter.return_value = mock_qs
        mock_qs.annotate.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter([])

        result = await load_user_issues_count([])

        assert result == []

    @patch("apps.github.api.internal.dataloaders.user.User")
    @pytest.mark.asyncio
    async def test_user_with_no_issues_returns_zero(self, mock_user):
        """A user with no issues yields 0."""
        users_data = [MagicMock(pk=1, items_count=None)]
        mock_qs = MagicMock()
        mock_user.objects.filter.return_value = mock_qs
        mock_qs.annotate.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter(users_data)

        result = await load_user_issues_count([1])

        assert result == [0]


class TestLoadUserReleasesCount:
    """Tests for load_user_releases_count."""

    @patch("apps.github.api.internal.dataloaders.user.User")
    @pytest.mark.asyncio
    async def test_returns_counts_grouped_by_user_id(self, mock_user):
        """Releases counts are grouped by user ID in the correct order."""
        users_data = [
            MagicMock(pk=1, items_count=2),
            MagicMock(pk=2, items_count=7),
        ]
        mock_qs = MagicMock()
        mock_user.objects.filter.return_value = mock_qs
        mock_qs.annotate.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter(users_data)

        result = await load_user_releases_count([1, 2])

        assert result == [2, 7]

    @patch("apps.github.api.internal.dataloaders.user.User")
    @pytest.mark.asyncio
    async def test_empty_user_ids(self, mock_user):
        """An empty user_ids list returns an empty list."""
        mock_qs = MagicMock()
        mock_user.objects.filter.return_value = mock_qs
        mock_qs.annotate.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter([])

        result = await load_user_releases_count([])

        assert result == []

    @patch("apps.github.api.internal.dataloaders.user.User")
    @pytest.mark.asyncio
    async def test_user_with_no_releases_returns_zero(self, mock_user):
        """A user with no releases yields 0."""
        users_data = [MagicMock(pk=1, items_count=None)]
        mock_qs = MagicMock()
        mock_user.objects.filter.return_value = mock_qs
        mock_qs.annotate.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter(users_data)

        result = await load_user_releases_count([1])

        assert result == [0]


class TestGetUserLoaders:
    """Tests for get_user_loaders."""

    def test_returns_mapping_with_all_loaders(self):
        """Factory returns a mapping with all loaders."""
        loaders = get_user_loaders()
        assert USER_BADGES_BY_USER_ID_LOADER in loaders
        assert USER_ISSUES_COUNT_LOADER in loaders
        assert USER_RELEASES_COUNT_LOADER in loaders
        assert isinstance(loaders[USER_BADGES_BY_USER_ID_LOADER], DataLoader)
        assert isinstance(loaders[USER_ISSUES_COUNT_LOADER], DataLoader)
        assert isinstance(loaders[USER_RELEASES_COUNT_LOADER], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_user_loaders()
        loaders2 = get_user_loaders()
        assert loaders1 is not loaders2
        for key in (
            USER_BADGES_BY_USER_ID_LOADER,
            USER_ISSUES_COUNT_LOADER,
            USER_RELEASES_COUNT_LOADER,
        ):
            assert loaders1[key] is not loaders2[key]

    def test_load_fn_is_correct(self):
        """Each loader is wired to its correct load function."""
        loaders = get_user_loaders()
        assert loaders[USER_BADGES_BY_USER_ID_LOADER].load_fn is load_user_badges_by_user_id
        assert loaders[USER_ISSUES_COUNT_LOADER].load_fn is load_user_issues_count
        assert loaders[USER_RELEASES_COUNT_LOADER].load_fn is load_user_releases_count
