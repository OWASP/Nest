"""Tests for pull request dataloaders."""

from unittest.mock import MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.pull_request import (
    RECENT_PULL_REQUESTS_BY_PROJECT_ID,
    get_pull_request_loaders,
    load_recent_pull_requests_by_project_id,
)


def _build_queryset_mock(mock_pull_request):
    """Wire up the chained mock queryset ending at order_by()."""
    mock_filter_result = mock_pull_request.objects.filter.return_value
    call = mock_filter_result.select_related.return_value
    return call.prefetch_related.return_value.order_by.return_value


class TestLoadRecentPullRequestsByProjectId:
    """Tests for load_recent_pull_requests_by_project_id."""

    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_pull_request):
        """Queryset is built with filter, select_related, prefetch_related, order_by, distinct."""
        mock_ordered = _build_queryset_mock(mock_pull_request)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([])

        await load_recent_pull_requests_by_project_id([(1, 5), (2, 5)])

        mock_pull_request.objects.filter.assert_called_once_with(repository__project__in=[1, 2])
        mock_filter_result = mock_pull_request.objects.filter.return_value
        mock_filter_result.select_related.assert_called_once_with(
            "author",
            "milestone",
            "repository__organization",
            "repository",
        )
        mock_select = mock_filter_result.select_related.return_value
        mock_select.prefetch_related.assert_called_once()
        mock_select.prefetch_related.return_value.order_by.assert_called_once_with("-created_at")
        mock_ordered.distinct.assert_called_once()

    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_maps_pull_requests_to_project_ids(self, mock_pull_request):
        """Pull requests are mapped to the projects that own the PR's repository."""
        project_1 = MagicMock(pk=1)
        project_2 = MagicMock(pk=2)
        pr_a = MagicMock()
        pr_a.repository.prefetched_projects = [project_1]
        pr_b = MagicMock()
        pr_b.repository.prefetched_projects = [project_2]

        mock_ordered = _build_queryset_mock(mock_pull_request)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([pr_a, pr_b])

        result = await load_recent_pull_requests_by_project_id([(1, 5), (2, 5)])

        assert result == [[pr_a], [pr_b]]

    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_limit_enforced_per_project(self, mock_pull_request):
        """Each project list is truncated to the configured limit."""
        project = MagicMock(pk=1)
        pull_requests = [MagicMock() for _ in range(5)]
        for pr in pull_requests:
            pr.repository.prefetched_projects = [project]

        mock_ordered = _build_queryset_mock(mock_pull_request)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter(pull_requests)

        result = await load_recent_pull_requests_by_project_id([(1, 3)])

        assert result == [[pull_requests[0], pull_requests[1], pull_requests[2]]]

    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_order_matches_keys_not_queryset(self, mock_pull_request):
        """The output order follows project_ids, not the queryset iteration order."""
        project_1 = MagicMock(pk=1)
        project_2 = MagicMock(pk=2)
        pr_b = MagicMock()
        pr_b.repository.prefetched_projects = [project_2]
        pr_a = MagicMock()
        pr_a.repository.prefetched_projects = [project_1]

        mock_ordered = _build_queryset_mock(mock_pull_request)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([pr_b, pr_a])

        result = await load_recent_pull_requests_by_project_id([(1, 5), (2, 5)])

        assert result == [[pr_a], [pr_b]]

    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_shared_repository_appears_in_each_project(self, mock_pull_request):
        """A repo shared between projects contributes the PR to each project."""
        project_1 = MagicMock(pk=1)
        project_2 = MagicMock(pk=2)
        pr = MagicMock()
        pr.repository.prefetched_projects = [project_1, project_2]

        mock_ordered = _build_queryset_mock(mock_pull_request)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([pr])

        result = await load_recent_pull_requests_by_project_id([(1, 5), (2, 5)])

        assert result == [[pr], [pr]]

    @pytest.mark.asyncio
    async def test_empty_keys(self):
        """An empty keys list returns an empty list."""
        result = await load_recent_pull_requests_by_project_id([])
        assert result == []

    @patch("apps.github.api.internal.dataloaders.pull_request.PullRequest")
    @pytest.mark.asyncio
    async def test_missing_project_returns_empty_list(self, mock_pull_request):
        """A project ID with no matching pull requests gets an empty list."""
        mock_ordered = _build_queryset_mock(mock_pull_request)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([])

        result = await load_recent_pull_requests_by_project_id([(99, 5)])

        assert result == [[]]


class TestGetPullRequestLoaders:
    """Tests for get_pull_request_loaders."""

    def test_returns_mapping(self):
        """Factory always returns a Mapping."""
        loaders = get_pull_request_loaders()
        assert RECENT_PULL_REQUESTS_BY_PROJECT_ID in loaders
        assert isinstance(loaders[RECENT_PULL_REQUESTS_BY_PROJECT_ID], DataLoader)

    def test_load_fn_is_load_recent_pull_requests_by_project_id(self):
        """The loader is wired to load_recent_pull_requests_by_project_id."""
        loaders = get_pull_request_loaders()
        loader = loaders[RECENT_PULL_REQUESTS_BY_PROJECT_ID]
        assert loader.load_fn is load_recent_pull_requests_by_project_id

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_pull_request_loaders()
        loaders2 = get_pull_request_loaders()
        assert loaders1 is not loaders2
        assert (
            loaders1[RECENT_PULL_REQUESTS_BY_PROJECT_ID]
            is not loaders2[RECENT_PULL_REQUESTS_BY_PROJECT_ID]
        )
