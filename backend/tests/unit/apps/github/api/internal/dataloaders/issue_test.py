"""Tests for issue dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.issue import (
    ISSUES_BY_REPOSITORY_ID_LOADER,
    ISSUES_COUNT_BY_PROJECT_ID,
    OPEN_ISSUES_COUNT_BY_PROJECT_ID,
    RECENT_ISSUES_BY_PROJECT_ID,
    get_issue_loaders,
    load_issues_by_repository_id,
    load_issues_count_by_project_id,
    load_open_issues_count_by_project_id,
    load_recent_issues_by_project_id,
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


class TestLoadOpenIssuesCountByProjectId:
    """Tests for load_open_issues_count_by_project_id."""

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Project")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_project, mock_get_result_by_keys):
        """Queryset is built with filter and only(pk, open_issues_count)."""
        project_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.only.return_value = mock_qs
        mock_get_result_by_keys.return_value = [0, 0, 0]

        await load_open_issues_count_by_project_id(project_ids)

        mock_project.objects.filter.assert_called_once_with(pk__in=project_ids)
        mock_project.objects.filter.return_value.only.assert_called_once_with(
            "pk", "open_issues_count"
        )

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Project")
    @pytest.mark.asyncio
    async def test_delegates_to_get_result_by_keys(self, mock_project, mock_get_result_by_keys):
        """get_result_by_keys receives the queryset, ids, and correct value_field."""
        project_ids = [10, 20]
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.only.return_value = mock_qs
        mock_get_result_by_keys.return_value = [3, 7]

        result = await load_open_issues_count_by_project_id(project_ids)

        mock_get_result_by_keys.assert_called_once_with(
            mock_qs, project_ids, key_field="pk", value_field="open_issues_count"
        )
        assert result == [3, 7]

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Project")
    @pytest.mark.asyncio
    async def test_zero_replaces_none(self, mock_project, mock_get_result_by_keys):
        """A None result is coerced to 0."""
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.only.return_value = mock_qs
        mock_get_result_by_keys.return_value = [None]

        result = await load_open_issues_count_by_project_id([99])

        assert result == [0]

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Project")
    @pytest.mark.asyncio
    async def test_empty_project_ids(self, mock_project, mock_get_result_by_keys):
        """An empty project_ids list returns an empty list."""
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.only.return_value = mock_qs
        mock_get_result_by_keys.return_value = []

        result = await load_open_issues_count_by_project_id([])

        assert result == []


class TestLoadIssuesCountByProjectId:
    """Tests for load_issues_count_by_project_id."""

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Repository")
    @patch("apps.github.api.internal.dataloaders.issue.Project")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_project, mock_repository, mock_get_result_by_keys
    ):
        """Queryset filters by pk__in and repositories__in subquery, then annotates."""
        project_ids = [1, 2, 3]
        mock_subq = MagicMock()
        mock_repository.objects.filter.return_value = mock_subq
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = [0, 0, 0]

        await load_issues_count_by_project_id(project_ids)

        mock_repository.objects.filter.assert_called_once_with(organization__isnull=False)
        mock_project.objects.filter.assert_called_once_with(
            pk__in=project_ids, repositories__in=mock_subq
        )
        mock_project.objects.filter.return_value.annotate.assert_called_once()

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Repository")
    @patch("apps.github.api.internal.dataloaders.issue.Project")
    @pytest.mark.asyncio
    async def test_delegates_to_get_result_by_keys(
        self, mock_project, mock_repository, mock_get_result_by_keys
    ):
        """get_result_by_keys receives the queryset, ids, and correct value_field."""
        project_ids = [10, 20]
        mock_subq = MagicMock()
        mock_repository.objects.filter.return_value = mock_subq
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = [4, 8]

        result = await load_issues_count_by_project_id(project_ids)

        mock_get_result_by_keys.assert_called_once_with(
            mock_qs, project_ids, key_field="pk", value_field="items_count"
        )
        assert result == [4, 8]

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Repository")
    @patch("apps.github.api.internal.dataloaders.issue.Project")
    @pytest.mark.asyncio
    async def test_zero_replaces_none(
        self, mock_project, mock_repository, mock_get_result_by_keys
    ):
        """A None result is coerced to 0."""
        mock_subq = MagicMock()
        mock_repository.objects.filter.return_value = mock_subq
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = [None]

        result = await load_issues_count_by_project_id([99])

        assert result == [0]

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Repository")
    @patch("apps.github.api.internal.dataloaders.issue.Project")
    @pytest.mark.asyncio
    async def test_empty_project_ids(self, mock_project, mock_repository, mock_get_result_by_keys):
        """An empty project_ids list returns an empty list."""
        mock_subq = MagicMock()
        mock_repository.objects.filter.return_value = mock_subq
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = []

        result = await load_issues_count_by_project_id([])

        assert result == []


class TestGetIssueLoaders:
    """Tests for get_issue_loaders."""

    def test_returns_mapping(self):
        """Factory always returns a Mapping."""
        loaders = get_issue_loaders()
        assert ISSUES_BY_REPOSITORY_ID_LOADER in loaders
        assert isinstance(loaders[ISSUES_BY_REPOSITORY_ID_LOADER], DataLoader)
        assert ISSUES_COUNT_BY_PROJECT_ID in loaders
        assert isinstance(loaders[ISSUES_COUNT_BY_PROJECT_ID], DataLoader)
        assert OPEN_ISSUES_COUNT_BY_PROJECT_ID in loaders
        assert isinstance(loaders[OPEN_ISSUES_COUNT_BY_PROJECT_ID], DataLoader)
        assert RECENT_ISSUES_BY_PROJECT_ID in loaders
        assert isinstance(loaders[RECENT_ISSUES_BY_PROJECT_ID], DataLoader)

    def test_load_fn_is_load_issues_by_repository_id(self):
        """The loader is wired to load_issues_by_repository_id."""
        loaders = get_issue_loaders()
        loader = loaders[ISSUES_BY_REPOSITORY_ID_LOADER]
        assert loader.load_fn is load_issues_by_repository_id

    def test_load_fn_is_load_issues_count_by_project_id(self):
        """The issues count loader is wired to load_issues_count_by_project_id."""
        loaders = get_issue_loaders()
        assert loaders[ISSUES_COUNT_BY_PROJECT_ID].load_fn is load_issues_count_by_project_id

    def test_load_fn_is_load_open_issues_count_by_project_id(self):
        """The open issues count loader is wired to load_open_issues_count_by_project_id."""
        loaders = get_issue_loaders()
        assert (
            loaders[OPEN_ISSUES_COUNT_BY_PROJECT_ID].load_fn
            is load_open_issues_count_by_project_id
        )

    def test_load_fn_is_load_recent_issues_by_project_id(self):
        """The loader is wired to load_recent_issues_by_project_id."""
        loaders = get_issue_loaders()
        loader = loaders[RECENT_ISSUES_BY_PROJECT_ID]
        assert loader.load_fn is load_recent_issues_by_project_id

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_issue_loaders()
        loaders2 = get_issue_loaders()
        assert loaders1 is not loaders2
        for key in [
            ISSUES_BY_REPOSITORY_ID_LOADER,
            ISSUES_COUNT_BY_PROJECT_ID,
            OPEN_ISSUES_COUNT_BY_PROJECT_ID,
            RECENT_ISSUES_BY_PROJECT_ID,
        ]:
            assert loaders1[key] is not loaders2[key]


class TestLoadRecentIssuesByProjectId:
    """Tests for load_recent_issues_by_project_id."""

    @staticmethod
    def _ordered_qs(mock_issue):
        """Return the mock queryset at the end of the issues chain."""
        call = mock_issue.objects.filter.return_value
        return call.annotate.return_value.filter.return_value.order_by.return_value

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Issue")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_issue, mock_get_results):
        """Queryset is built with filter, annotate, filter(row_number__lte), order_by."""
        mock_ordered = self._ordered_qs(mock_issue)
        mock_get_results.return_value = [[], []]

        await load_recent_issues_by_project_id([(1, 5), (2, 5)])

        mock_issue.objects.filter.assert_called_once_with(repository__project__in=[1, 2])
        mock_issue.objects.filter.return_value.annotate.assert_called_once()
        mock_issue.objects.filter.return_value.annotate.return_value.filter.assert_called_once_with(
            row_number__lte=5
        )
        mock_issue.objects.filter.return_value.annotate.return_value.filter.return_value.order_by.assert_called_once_with(
            "project_id", "-created_at"
        )
        mock_get_results.assert_called_once_with(mock_ordered, [1, 2], key_field="project_id")

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Issue")
    @pytest.mark.asyncio
    async def test_maps_issues_to_project_ids(self, mock_issue, mock_get_results):
        """Issues are mapped to the projects that own the issue's repository."""
        issue_a = MagicMock()
        issue_b = MagicMock()
        mock_get_results.return_value = [[issue_a], [issue_b]]

        result = await load_recent_issues_by_project_id([(1, 5), (2, 5)])

        assert result == [[issue_a], [issue_b]]

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Issue")
    @pytest.mark.asyncio
    async def test_limit_enforced_per_project(self, mock_issue, mock_get_results):
        """Each project list is truncated to the configured limit."""
        issues = [MagicMock() for _ in range(5)]
        mock_get_results.return_value = [issues[:3]]

        result = await load_recent_issues_by_project_id([(1, 3)])

        assert result == [issues[:3]]

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Issue")
    @pytest.mark.asyncio
    async def test_order_matches_keys_not_queryset(self, mock_issue, mock_get_results):
        """The output order follows project_ids, not the queryset iteration order."""
        issue_a = MagicMock()
        issue_b = MagicMock()
        mock_get_results.return_value = [[issue_a], [issue_b]]

        result = await load_recent_issues_by_project_id([(1, 5), (2, 5)])

        assert result == [[issue_a], [issue_b]]

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Issue")
    @pytest.mark.asyncio
    async def test_shared_repository_appears_in_each_project(self, mock_issue, mock_get_results):
        """A repo shared between projects contributes the issue to each project."""
        issue = MagicMock()
        mock_get_results.return_value = [[issue], [issue]]

        result = await load_recent_issues_by_project_id([(1, 5), (2, 5)])

        assert result == [[issue], [issue]]

    @pytest.mark.asyncio
    async def test_empty_keys(self):
        """An empty keys list returns an empty list."""
        result = await load_recent_issues_by_project_id([])
        assert result == []

    @patch(
        "apps.github.api.internal.dataloaders.issue.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.issue.Issue")
    @pytest.mark.asyncio
    async def test_missing_project_returns_empty_list(self, mock_issue, mock_get_results):
        """A project ID with no matching issues gets an empty list."""
        mock_get_results.return_value = [[]]

        result = await load_recent_issues_by_project_id([(99, 5)])

        assert result == [[]]
