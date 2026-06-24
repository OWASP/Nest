"""Tests for user dataloaders."""

from unittest.mock import MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.user import (
    USER_BADGES_BY_USER_ID_LOADER,
    get_user_loaders,
    load_user_badges_by_user_id,
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


class TestGetUserLoaders:
    """Tests for get_user_loaders."""

    def test_returns_mapping_with_badge_loader(self):
        """Factory returns a mapping with the badge loader."""
        loaders = get_user_loaders()
        assert USER_BADGES_BY_USER_ID_LOADER in loaders
        assert isinstance(loaders[USER_BADGES_BY_USER_ID_LOADER], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_user_loaders()
        loaders2 = get_user_loaders()
        assert loaders1 is not loaders2
        assert (
            loaders1[USER_BADGES_BY_USER_ID_LOADER] is not loaders2[USER_BADGES_BY_USER_ID_LOADER]
        )

    def test_load_fn_is_load_user_badges_by_user_id(self):
        """The badge loader is wired to load_user_badges_by_user_id."""
        loaders = get_user_loaders()
        loader = loaders[USER_BADGES_BY_USER_ID_LOADER]
        assert loader.load_fn is load_user_badges_by_user_id
