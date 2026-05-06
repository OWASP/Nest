"""Tests for the interested_users dataloader."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.interested_users import (
    load_interested_users,
    make_interested_users_loader,
)


class TestLoadInterestedUsers:
    """Tests for load_interested_users."""

    @patch(
        "apps.github.api.internal.dataloaders.interested_users.results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.interested_users.IssueUserInterest")
    def test_builds_queryset_with_correct_chain(self, mock_iui, mock_results_by_keys):
        """Queryset is built with select_related, filter, and order_by in the right order."""
        issue_ids = [1, 2, 3]
        mock_queryset = MagicMock()
        mock_iui.objects.select_related.return_value.filter.return_value.order_by.return_value = (
            mock_queryset
        )
        mock_results_by_keys.return_value = [[], [], []]

        asyncio.run(load_interested_users(issue_ids))

        mock_iui.objects.select_related.assert_called_once_with("user__owasp_profile")
        mock_filter = mock_iui.objects.select_related.return_value.filter
        mock_filter.assert_called_once_with(issue_id__in=issue_ids)
        mock_filter.return_value.order_by.assert_called_once_with("user__login")

    @patch(
        "apps.github.api.internal.dataloaders.interested_users.results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.interested_users.IssueUserInterest")
    def test_delegates_to_results_by_keys_correct_args(self, mock_iui, mock_results_by_keys):
        """results_by_keys receives the queryset, issue_ids, and correct field names."""
        issue_ids = [10, 20]
        mock_queryset = MagicMock()
        mock_iui.objects.select_related.return_value.filter.return_value.order_by.return_value = (
            mock_queryset
        )
        mock_results_by_keys.return_value = [[], []]

        asyncio.run(load_interested_users(issue_ids))

        mock_results_by_keys.assert_called_once_with(
            mock_queryset, issue_ids, key_field="issue_id", value_field="user"
        )

    @patch(
        "apps.github.api.internal.dataloaders.interested_users.results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.interested_users.IssueUserInterest")
    def test_returns_result_from_results_by_keys(self, mock_iui, mock_results_by_keys):
        """The return value is exactly what results_by_keys resolves to."""
        mock_user_a = MagicMock()
        mock_user_b = MagicMock()
        expected = [[mock_user_a, mock_user_b], [], [mock_user_a]]
        mock_results_by_keys.return_value = expected

        result = asyncio.run(load_interested_users([1, 2, 3]))

        assert result is expected

    @patch(
        "apps.github.api.internal.dataloaders.interested_users.results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.interested_users.IssueUserInterest")
    def test_empty_issue_ids(self, mock_iui, mock_results_by_keys):
        """An empty issue_ids list results in an empty filter and empty return."""
        mock_iui.objects.select_related.return_value.filter.return_value.order_by.return_value = (
            MagicMock()
        )
        mock_results_by_keys.return_value = []

        result = asyncio.run(load_interested_users([]))

        mock_iui.objects.select_related.return_value.filter.assert_called_once_with(
            issue_id__in=[]
        )
        assert result == []

    @patch(
        "apps.github.api.internal.dataloaders.interested_users.results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.interested_users.IssueUserInterest")
    def test_single_issue_id(self, mock_iui, mock_results_by_keys):
        """A single-element list is handled correctly end-to-end."""
        mock_user = MagicMock()
        mock_iui.objects.select_related.return_value.filter.return_value.order_by.return_value = (
            MagicMock()
        )
        mock_results_by_keys.return_value = [[mock_user]]

        result = asyncio.run(load_interested_users([42]))

        mock_iui.objects.select_related.return_value.filter.assert_called_once_with(
            issue_id__in=[42]
        )
        assert result == [[mock_user]]

    @patch(
        "apps.github.api.internal.dataloaders.interested_users.results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.interested_users.IssueUserInterest")
    def test_preserves_issue_ids_order(self, mock_iui, mock_results_by_keys):
        """The issue_ids list is forwarded to results_by_keys unchanged, preserving order."""
        issue_ids = [30, 10, 20]
        mock_iui.objects.select_related.return_value.filter.return_value.order_by.return_value = (
            MagicMock()
        )
        mock_results_by_keys.return_value = [[], [], []]

        asyncio.run(load_interested_users(issue_ids))

        _, positional_args, _ = mock_results_by_keys.mock_calls[0]
        assert positional_args[1] is issue_ids


class TestMakeInterestedUsersLoader:
    """Tests for make_interested_users_loader."""

    def test_returns_dataloader_instance(self):
        """Factory always returns a DataLoader."""
        loader = make_interested_users_loader()
        assert isinstance(loader, DataLoader)

    def test_returns_new_instance_on_each_call(self):
        """Each call produces a distinct DataLoader for per-request isolation."""
        loader1 = make_interested_users_loader()
        loader2 = make_interested_users_loader()
        assert loader1 is not loader2

    def test_load_fn_is_load_interested_users(self):
        """The DataLoader is wired to load_interested_users."""
        loader = make_interested_users_loader()
        assert loader.load_fn is load_interested_users
