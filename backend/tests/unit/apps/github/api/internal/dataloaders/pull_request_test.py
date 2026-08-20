"""Tests for pull request dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.pull_request import (
    PULL_REQUESTS_BY_ISSUE_ID_LOADER,
    RECENT_PULL_REQUESTS_BY_PROJECT_ID_LOADER,
    get_pull_request_loaders,
    load_pull_requests_by_issue_id,
    load_recent_pull_requests_by_project_id,
)


def _build_queryset_mock(mock_pull_request):
    """Wire up the chained mock queryset ending at order_by()."""
    call = mock_pull_request.objects.filter.return_value
    return call.annotate.return_value.filter.return_value.order_by.return_value


class TestLoadRecentPullRequestsByProjectId:
    """Tests for load_recent_pull_requests_by_project_id."""

    @patch(
        "apps.github.api.internal.dataloaders.pull_request.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_pull_request, mock_get_results):
        """Queryset is built with filter, annotate, filter(row_number__lte), order_by."""
        mock_ordered = _build_queryset_mock(mock_pull_request)
        mock_get_results.return_value = [[], []]

        await load_recent_pull_requests_by_project_id([(1, 5), (2, 5)])

        mock_pull_request.objects.filter.assert_called_once_with(repository__project__in=[1, 2])
        mock_pull_request.objects.filter.return_value.annotate.assert_called_once()
        mock_pull_request.objects.filter.return_value.annotate.return_value.filter.assert_called_once_with(
            row_number__lte=5
        )
        mock_pull_request.objects.filter.return_value.annotate.return_value.filter.return_value.order_by.assert_called_once_with(
            "project_id", "-created_at"
        )
        mock_get_results.assert_called_once_with(mock_ordered, [1, 2], key_field="project_id")

    @patch(
        "apps.github.api.internal.dataloaders.pull_request.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_maps_pull_requests_to_project_ids(self, mock_pull_request, mock_get_results):
        """Pull requests are mapped to the projects that own the PR's repository."""
        pr_a = MagicMock()
        pr_b = MagicMock()
        mock_get_results.return_value = [[pr_a], [pr_b]]

        result = await load_recent_pull_requests_by_project_id([(1, 5), (2, 5)])

        assert result == [[pr_a], [pr_b]]

    @patch(
        "apps.github.api.internal.dataloaders.pull_request.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_limit_enforced_per_project(self, mock_pull_request, mock_get_results):
        """Each project list is truncated to the configured limit."""
        pull_requests = [MagicMock() for _ in range(5)]
        mock_get_results.return_value = [pull_requests[:3]]

        result = await load_recent_pull_requests_by_project_id([(1, 3)])

        assert result == [pull_requests[:3]]

    @patch(
        "apps.github.api.internal.dataloaders.pull_request.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_order_matches_keys_not_queryset(self, mock_pull_request, mock_get_results):
        """The output order follows project_ids, not the queryset iteration order."""
        pr_a = MagicMock()
        pr_b = MagicMock()
        mock_get_results.return_value = [[pr_a], [pr_b]]

        result = await load_recent_pull_requests_by_project_id([(1, 5), (2, 5)])

        assert result == [[pr_a], [pr_b]]

    @patch(
        "apps.github.api.internal.dataloaders.pull_request.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_shared_repository_appears_in_each_project(
        self, mock_pull_request, mock_get_results
    ):
        """A repo shared between projects contributes the PR to each project."""
        pr = MagicMock()
        mock_get_results.return_value = [[pr], [pr]]

        result = await load_recent_pull_requests_by_project_id([(1, 5), (2, 5)])

        assert result == [[pr], [pr]]

    @pytest.mark.asyncio
    async def test_empty_keys(self):
        """An empty keys list returns an empty list."""
        result = await load_recent_pull_requests_by_project_id([])
        assert result == []

    @patch(
        "apps.github.api.internal.dataloaders.pull_request.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_missing_project_returns_empty_list(self, mock_pull_request, mock_get_results):
        """A project ID with no matching pull requests gets an empty list."""
        mock_get_results.return_value = [[]]

        result = await load_recent_pull_requests_by_project_id([(99, 5)])

        assert result == [[]]


class TestLoadPullRequestsByIssueId:
    """Tests for load_pull_requests_by_issue_id."""

    @patch(
        "apps.github.api.internal.dataloaders.pull_request.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_pull_request, mock_get_results):
        """Queryset is built with filter, annotate, filter(offset/limit), and order_by."""
        mock_ordered = _build_queryset_mock(mock_pull_request)
        mock_get_results.return_value = [[], []]

        await load_pull_requests_by_issue_id([(1, 4, 0), (2, 4, 0)])

        mock_pull_request.objects.filter.assert_called_once_with(related_issues__id__in=[1, 2])
        mock_pull_request.objects.filter.return_value.annotate.assert_called_once()
        mock_pull_request.objects.filter.return_value.annotate.return_value.filter.assert_called_once_with(
            row_number__gt=0, row_number__lte=4
        )
        mock_pull_request.objects.filter.return_value.annotate.return_value.filter.return_value.order_by.assert_called_once_with(
            "issue_id", "-created_at"
        )
        mock_get_results.assert_called_once_with(mock_ordered, [1, 2], key_field="issue_id")

    @patch(
        "apps.github.api.internal.dataloaders.pull_request.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_applies_offset_to_window_filter(self, mock_pull_request, mock_get_results):
        """The offset shifts the row_number window boundaries."""
        mock_get_results.return_value = [[]]

        await load_pull_requests_by_issue_id([(1, 4, 4)])

        mock_pull_request.objects.filter.return_value.annotate.return_value.filter.assert_called_once_with(
            row_number__gt=4, row_number__lte=8
        )

    @patch(
        "apps.github.api.internal.dataloaders.pull_request.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_maps_pull_requests_to_issue_ids(self, mock_pull_request, mock_get_results):
        """Pull requests are mapped to the issues they are related to."""
        pr_a = MagicMock()
        pr_b = MagicMock()
        mock_get_results.return_value = [[pr_a], [pr_b]]

        result = await load_pull_requests_by_issue_id([(1, 4, 0), (2, 4, 0)])

        assert result == [[pr_a], [pr_b]]

    @pytest.mark.asyncio
    async def test_empty_keys(self):
        """An empty keys list returns an empty list."""
        result = await load_pull_requests_by_issue_id([])
        assert result == []

    @patch(
        "apps.github.api.internal.dataloaders.pull_request.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_missing_issue_returns_empty_list(self, mock_pull_request, mock_get_results):
        """An issue ID with no matching pull requests gets an empty list."""
        mock_get_results.return_value = [[]]

        result = await load_pull_requests_by_issue_id([(99, 4, 0)])

        assert result == [[]]


class TestGetPullRequestLoaders:
    """Tests for get_pull_request_loaders."""

    def test_returns_mapping(self):
        """Factory always returns a Mapping."""
        loaders = get_pull_request_loaders()
        assert PULL_REQUESTS_BY_ISSUE_ID_LOADER in loaders
        assert RECENT_PULL_REQUESTS_BY_PROJECT_ID_LOADER in loaders
        assert isinstance(loaders[PULL_REQUESTS_BY_ISSUE_ID_LOADER], DataLoader)
        assert isinstance(loaders[RECENT_PULL_REQUESTS_BY_PROJECT_ID_LOADER], DataLoader)

    def test_load_fn_is_load_pull_requests_by_issue_id(self):
        """The by-issue-id loader is wired to load_pull_requests_by_issue_id."""
        loaders = get_pull_request_loaders()
        loader = loaders[PULL_REQUESTS_BY_ISSUE_ID_LOADER]
        assert loader.load_fn is load_pull_requests_by_issue_id

    def test_load_fn_is_load_recent_pull_requests_by_project_id(self):
        """The loader is wired to load_recent_pull_requests_by_project_id."""
        loaders = get_pull_request_loaders()
        loader = loaders[RECENT_PULL_REQUESTS_BY_PROJECT_ID_LOADER]
        assert loader.load_fn is load_recent_pull_requests_by_project_id

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_pull_request_loaders()
        loaders2 = get_pull_request_loaders()
        assert loaders1 is not loaders2
        assert (
            loaders1[PULL_REQUESTS_BY_ISSUE_ID_LOADER]
            is not loaders2[PULL_REQUESTS_BY_ISSUE_ID_LOADER]
        )
        assert (
            loaders1[RECENT_PULL_REQUESTS_BY_PROJECT_ID_LOADER]
            is not loaders2[RECENT_PULL_REQUESTS_BY_PROJECT_ID_LOADER]
        )
