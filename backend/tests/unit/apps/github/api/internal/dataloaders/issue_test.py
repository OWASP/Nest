"""Tests for issue dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.issue import (
    ISSUES_BY_REPOSITORY_ID_LOADER,
    get_issue_loaders,
    load_issues_by_repository_id,
)


class TestLoadIssuesByRepositoryId:
    """Tests for load_issues_by_repository_id."""

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Issue")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_issue, mock_get_results_by_keys):
        """Queryset is built with filter, annotate, and order_by."""
        keys = [(1, 5), (2, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_issue.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], []]

        await load_issues_by_repository_id(keys)

        mock_issue.objects.filter.assert_called_once_with(repository_id__in=[1, 2])
        mock_filter.annotate.assert_called_once()
        mock_filter.annotate.return_value.filter.assert_called_once_with(row_number__lte=5)
        mock_filter.annotate.return_value.filter.return_value.order_by.assert_called_once_with(
            "repository_id", "-created_at"
        )

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Issue")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys(self, mock_issue, mock_get_results_by_keys):
        """get_results_by_keys receives the queryset, ids, and correct key_field."""
        keys = [(10, 5), (20, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_issue.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], []]

        await load_issues_by_repository_id(keys)

        mock_get_results_by_keys.assert_called_once_with(
            mock_qs, [10, 20], key_field="repository_id"
        )

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Issue")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_issue, mock_get_results_by_keys
    ):
        """The return value is what get_results_by_keys resolves to."""
        keys = [(1, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_issue.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_issue_obj = MagicMock()
        expected = [[mock_issue_obj]]
        mock_get_results_by_keys.return_value = expected

        result = await load_issues_by_repository_id(keys)

        assert result == expected

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Issue")
    @pytest.mark.asyncio
    async def test_empty_keys(self, mock_issue, mock_get_results_by_keys):
        """An empty keys list returns an empty list."""
        mock_get_results_by_keys.return_value = []

        result = await load_issues_by_repository_id([])

        assert result == []

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Issue")
    @pytest.mark.asyncio
    async def test_window_filter_enforces_limit(self, mock_issue, mock_get_results_by_keys):
        """The window function filter enforces the limit."""
        keys = [(1, 3)]
        mock_qs = MagicMock()
        mock_filter = mock_issue.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[MagicMock(), MagicMock(), MagicMock()]]

        result = await load_issues_by_repository_id(keys)

        mock_filter.annotate.return_value.filter.assert_called_once_with(row_number__lte=3)
        assert len(result[0]) == 3


class TestGetIssueLoaders:
    """Tests for get_issue_loaders."""

    def test_returns_mapping(self):
        """Factory always returns a Mapping."""
        loaders = get_issue_loaders()
        assert ISSUES_BY_REPOSITORY_ID_LOADER in loaders
        assert isinstance(loaders[ISSUES_BY_REPOSITORY_ID_LOADER], DataLoader)

    def test_load_fn_is_load_issues_by_repository_id(self):
        """The loader is wired to load_issues_by_repository_id."""
        loaders = get_issue_loaders()
        loader = loaders[ISSUES_BY_REPOSITORY_ID_LOADER]
        assert loader.load_fn is load_issues_by_repository_id

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_issue_loaders()
        loaders2 = get_issue_loaders()
        assert loaders1 is not loaders2
        assert (
            loaders1[ISSUES_BY_REPOSITORY_ID_LOADER]
            is not loaders2[ISSUES_BY_REPOSITORY_ID_LOADER]
        )
