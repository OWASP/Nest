"""Tests for the interested_users dataloader."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.mentorship.api.internal.dataloaders.interested_users import (
    INTERESTED_USERS_BY_ISSUE_ID_LOADER,
    get_interested_users_loaders,
    load_interested_users_by_issue_id,
)


class TestLoadInterestedUsers:
    """Tests for load_interested_users."""

    @patch(
        "apps.mentorship.api.internal.dataloaders.interested_users.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.interested_users.IssueUserInterest")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_interested, mock_get_results_by_keys
    ):
        """Queryset is built with select_related, filter, and order_by in the right order."""
        issue_ids = [1, 2, 3]
        mock_queryset = MagicMock()
        mock_interested_filter = mock_interested.objects.select_related.return_value.filter
        mock_interested_filter.return_value.order_by.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_interested_users_by_issue_id(issue_ids)

        mock_interested.objects.select_related.assert_called_once_with("user__owasp_profile")
        mock_filter = mock_interested.objects.select_related.return_value.filter
        mock_filter.assert_called_once_with(issue_id__in=issue_ids)
        mock_filter.return_value.order_by.assert_called_once_with("user__login")

    @patch(
        "apps.mentorship.api.internal.dataloaders.interested_users.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.interested_users.IssueUserInterest")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_interested, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, issue_ids, and correct field names."""
        issue_ids = [10, 20]
        mock_queryset = MagicMock()
        mock_interested_filter = mock_interested.objects.select_related.return_value.filter
        mock_interested_filter.return_value.order_by.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], []]

        await load_interested_users_by_issue_id(issue_ids)

        mock_get_results_by_keys.assert_called_once_with(
            mock_queryset, issue_ids, key_field="issue_id", value_field="user"
        )

    @patch(
        "apps.mentorship.api.internal.dataloaders.interested_users.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.interested_users.IssueUserInterest")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_interested, mock_get_results_by_keys
    ):
        """The return value is exactly what get_results_by_keys resolves to."""
        mock_user_a = MagicMock()
        mock_user_b = MagicMock()
        expected = [[mock_user_a, mock_user_b], [], [mock_user_a]]
        mock_get_results_by_keys.return_value = expected

        result = await load_interested_users_by_issue_id([1, 2, 3])

        assert result is expected

    @patch(
        "apps.mentorship.api.internal.dataloaders.interested_users.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.interested_users.IssueUserInterest")
    @pytest.mark.asyncio
    async def test_empty_issue_ids(self, mock_interested, mock_get_results_by_keys):
        """An empty issue_ids list results in an empty filter and empty return."""
        mock_interested_filter = mock_interested.objects.select_related.return_value.filter
        mock_interested_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_interested_users_by_issue_id([])

        mock_interested.objects.select_related.return_value.filter.assert_called_once_with(
            issue_id__in=[]
        )
        assert result == []

    @patch(
        "apps.mentorship.api.internal.dataloaders.interested_users.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.interested_users.IssueUserInterest")
    @pytest.mark.asyncio
    async def test_single_issue_id(self, mock_interested, mock_get_results_by_keys):
        """A single-element list is handled correctly end-to-end."""
        mock_user = MagicMock()
        mock_interested_filter = mock_interested.objects.select_related.return_value.filter
        mock_interested_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[mock_user]]

        result = await load_interested_users_by_issue_id([42])

        mock_interested.objects.select_related.return_value.filter.assert_called_once_with(
            issue_id__in=[42]
        )
        assert result == [[mock_user]]

    @patch(
        "apps.mentorship.api.internal.dataloaders.interested_users.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.interested_users.IssueUserInterest")
    @pytest.mark.asyncio
    async def test_preserves_issue_ids_order(self, mock_interested, mock_get_results_by_keys):
        """The issue_ids list is forwarded to get_results_by_keys unchanged, preserving order."""
        issue_ids = [30, 10, 20]
        mock_interested_filter = mock_interested.objects.select_related.return_value.filter
        mock_interested_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_interested_users_by_issue_id(issue_ids)

        _, positional_args, _ = mock_get_results_by_keys.mock_calls[0]
        assert positional_args[1] is issue_ids


class TestMakeInterestedUsersLoader:
    """Tests for get_interested_users_loaders."""

    def test_returns_mapping(self):
        """Factory always returns a Mapping."""
        loaders = get_interested_users_loaders()
        assert INTERESTED_USERS_BY_ISSUE_ID_LOADER in loaders
        assert isinstance(loaders[INTERESTED_USERS_BY_ISSUE_ID_LOADER], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_interested_users_loaders()
        loaders2 = get_interested_users_loaders()
        assert loaders1 is not loaders2
        assert (
            loaders1[INTERESTED_USERS_BY_ISSUE_ID_LOADER]
            is not loaders2[INTERESTED_USERS_BY_ISSUE_ID_LOADER]
        )

    def test_load_fn_is_load_interested_users_by_issue_id(self):
        """The by-issue-id DataLoader is wired to load_interested_users_by_issue_id."""
        loaders = get_interested_users_loaders()
        loader = loaders[INTERESTED_USERS_BY_ISSUE_ID_LOADER]
        assert loader.load_fn is load_interested_users_by_issue_id
