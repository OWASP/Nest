"""Tests for project dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.owasp.api.internal.dataloaders.project import (
    HEALTH_METRICS_LATEST_BY_PROJECT_ID,
    HEALTH_METRICS_LIST_BY_PROJECT_ID,
    ISSUES_COUNT_BY_PROJECT_ID,
    OPEN_ISSUES_COUNT_BY_PROJECT_ID,
    PROJECT_BY_REPOSITORY_ID_LOADER,
    REPOSITORIES_COUNT_BY_PROJECT_ID,
    get_project_loaders,
    load_health_metrics_latest_by_project_id,
    load_health_metrics_list_by_project_id,
    load_issues_count_by_project_id,
    load_open_issues_count_by_project_id,
    load_projects_by_repository_id,
    load_repositories_count_by_project_id,
)


class TestLoadProjectsByRepositoryId:
    """Tests for load_projects_by_repository_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_m2m_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_project, mock_get_m2m_results_by_keys
    ):
        """Queryset is built with filter, prefetch_related, order_by, distinct."""
        repository_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_filter = mock_project.objects.filter.return_value
        mock_filter.prefetch_related.return_value.order_by.return_value.distinct.return_value = (
            mock_qs
        )
        mock_get_m2m_results_by_keys.return_value = [[], [], []]

        await load_projects_by_repository_id(repository_ids)

        mock_project.objects.filter.assert_called_once_with(repositories__in=repository_ids)
        mock_filter.prefetch_related.assert_called_once_with("repositories")
        mock_filter.prefetch_related.return_value.order_by.assert_called_once_with("pk")
        mock_distinct = mock_filter.prefetch_related.return_value.order_by.return_value
        mock_distinct.distinct.assert_called_once()

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_m2m_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_delegates_to_get_m2m_results_by_keys_correct_args(
        self, mock_project, mock_get_m2m_results_by_keys
    ):
        """get_m2m_results_by_keys receives the queryset, ids, and correct fields."""
        repository_ids = [10, 20]
        mock_qs = MagicMock()
        mock_filter = mock_project.objects.filter.return_value
        mock_filter.prefetch_related.return_value.order_by.return_value.distinct.return_value = (
            mock_qs
        )
        mock_get_m2m_results_by_keys.return_value = [[], []]

        await load_projects_by_repository_id(repository_ids)

        mock_get_m2m_results_by_keys.assert_called_once_with(
            mock_qs, repository_ids, m2m_field="repositories", key_field="pk"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_m2m_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_returns_first_project_or_none(self, mock_project, mock_get_m2m_results_by_keys):
        """First project from each group is returned, or None if empty."""
        mock_qs = MagicMock()
        mock_filter = mock_project.objects.filter.return_value
        mock_filter.prefetch_related.return_value.order_by.return_value.distinct.return_value = (
            mock_qs
        )
        mock_project_a = MagicMock()
        mock_project_b = MagicMock()
        mock_get_m2m_results_by_keys.return_value = [
            [mock_project_a, mock_project_b],
            [],
            [mock_project_b],
        ]

        result = await load_projects_by_repository_id([1, 2, 3])

        assert result == [mock_project_a, None, mock_project_b]

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_m2m_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_empty_repository_ids(self, mock_project, mock_get_m2m_results_by_keys):
        """An empty repository_ids list returns an empty list."""
        mock_qs = MagicMock()
        mock_filter = mock_project.objects.filter.return_value
        mock_filter.prefetch_related.return_value.order_by.return_value.distinct.return_value = (
            mock_qs
        )
        mock_get_m2m_results_by_keys.return_value = []

        result = await load_projects_by_repository_id([])

        assert result == []

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_m2m_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_returns_none_when_no_project_found(
        self, mock_project, mock_get_m2m_results_by_keys
    ):
        """A repository ID with no matching project returns None."""
        mock_qs = MagicMock()
        mock_filter = mock_project.objects.filter.return_value
        mock_filter.prefetch_related.return_value.order_by.return_value.distinct.return_value = (
            mock_qs
        )
        mock_get_m2m_results_by_keys.return_value = [[]]

        result = await load_projects_by_repository_id([99])

        assert result == [None]


class TestLoadHealthMetricsListByProjectId:
    """Tests for load_health_metrics_list_by_project_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.ProjectHealthMetrics")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_metrics, mock_get_results_by_keys
    ):
        """Queryset is built with filter, annotate, filter(RowNumber), order_by."""
        keys = [(1, 5), (2, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_metrics.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], []]

        await load_health_metrics_list_by_project_id(keys)

        mock_metrics.objects.filter.assert_called_once_with(project_id__in=[1, 2])
        mock_filter.annotate.assert_called_once()
        mock_filter.annotate.return_value.filter.assert_called_once_with(row_number__lte=5)
        mock_filter.annotate.return_value.filter.return_value.order_by.assert_called_once_with(
            "project_id", "nest_created_at"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.ProjectHealthMetrics")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys(self, mock_metrics, mock_get_results_by_keys):
        """get_results_by_keys receives the queryset, ids, and correct key_field."""
        keys = [(10, 5), (20, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_metrics.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], []]

        await load_health_metrics_list_by_project_id(keys)

        mock_get_results_by_keys.assert_called_once_with(mock_qs, [10, 20], key_field="project_id")

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.ProjectHealthMetrics")
    @pytest.mark.asyncio
    async def test_window_filter_enforces_limit(self, mock_metrics, mock_get_results_by_keys):
        """The window function filter enforces the limit."""
        keys = [(1, 3)]
        mock_qs = MagicMock()
        mock_filter = mock_metrics.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[MagicMock(), MagicMock(), MagicMock()]]

        result = await load_health_metrics_list_by_project_id(keys)

        mock_filter.annotate.return_value.filter.assert_called_once_with(row_number__lte=3)
        assert len(result[0]) == 3

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.ProjectHealthMetrics")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_metrics, mock_get_results_by_keys
    ):
        """The return value is what get_results_by_keys resolves to."""
        keys = [(1, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_metrics.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_metric = MagicMock()
        expected = [[mock_metric]]
        mock_get_results_by_keys.return_value = expected

        result = await load_health_metrics_list_by_project_id(keys)

        assert result == expected

    @pytest.mark.asyncio
    async def test_empty_keys(self):
        """An empty keys list returns an empty list."""
        result = await load_health_metrics_list_by_project_id([])

        assert result == []


class TestLoadHealthMetricsLatestByProjectId:
    """Tests for load_health_metrics_latest_by_project_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.ProjectHealthMetrics")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_metrics, mock_get_result_by_keys):
        """Queryset is built with filter, distinct, order_by."""
        project_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_filter = mock_metrics.objects.filter.return_value
        mock_filter.distinct.return_value.order_by.return_value = mock_qs
        mock_get_result_by_keys.return_value = [None, None, None]

        await load_health_metrics_latest_by_project_id(project_ids)

        mock_metrics.objects.filter.assert_called_once_with(project_id__in=project_ids)
        mock_filter.distinct.assert_called_once_with("project_id")
        mock_filter.distinct.return_value.order_by.assert_called_once_with(
            "project_id", "-nest_created_at"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.ProjectHealthMetrics")
    @pytest.mark.asyncio
    async def test_delegates_to_get_result_by_keys(self, mock_metrics, mock_get_result_by_keys):
        """get_result_by_keys receives the queryset, ids, and correct key_field."""
        project_ids = [10, 20]
        mock_qs = MagicMock()
        mock_filter = mock_metrics.objects.filter.return_value
        mock_filter.distinct.return_value.order_by.return_value = mock_qs
        mock_get_result_by_keys.return_value = [None, None]

        await load_health_metrics_latest_by_project_id(project_ids)

        mock_get_result_by_keys.assert_called_once_with(
            mock_qs, project_ids, key_field="project_id"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.ProjectHealthMetrics")
    @pytest.mark.asyncio
    async def test_returns_none_when_no_metric(self, mock_metrics, mock_get_result_by_keys):
        """A project ID with no matching metric gets None."""
        mock_qs = MagicMock()
        mock_filter = mock_metrics.objects.filter.return_value
        mock_filter.distinct.return_value.order_by.return_value = mock_qs
        mock_get_result_by_keys.return_value = [None]

        result = await load_health_metrics_latest_by_project_id([99])

        assert result == [None]

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.ProjectHealthMetrics")
    @pytest.mark.asyncio
    async def test_empty_project_ids(self, mock_metrics, mock_get_result_by_keys):
        """An empty project_ids list returns an empty list."""
        mock_qs = MagicMock()
        mock_filter = mock_metrics.objects.filter.return_value
        mock_filter.distinct.return_value.order_by.return_value = mock_qs
        mock_get_result_by_keys.return_value = []

        result = await load_health_metrics_latest_by_project_id([])

        assert result == []


class TestLoadOpenIssuesCountByProjectId:
    """Tests for load_open_issues_count_by_project_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
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
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
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
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_zero_replaces_none(self, mock_project, mock_get_result_by_keys):
        """A None result is coerced to 0."""
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.only.return_value = mock_qs
        mock_get_result_by_keys.return_value = [None]

        result = await load_open_issues_count_by_project_id([99])

        assert result == [0]

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
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
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_project, mock_get_result_by_keys):
        """Queryset is built with filter and annotate(Count with filter)."""
        project_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = [0, 0, 0]

        await load_issues_count_by_project_id(project_ids)

        mock_project.objects.filter.assert_called_once_with(pk__in=project_ids)
        mock_project.objects.filter.return_value.annotate.assert_called_once()

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.ISSUES_COUNT_FILTER")
    @patch("apps.owasp.api.internal.dataloaders.project.Count")
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_uses_filtered_count(
        self, mock_project, mock_count, mock_filter, mock_get_result_by_keys
    ):
        """Count is called with the open-issues filter for repositories__issues."""
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = [0]

        await load_issues_count_by_project_id([1])

        mock_count.assert_called_once_with("repositories__issues", filter=mock_filter)
        mock_project.objects.filter.return_value.annotate.assert_called_once_with(
            items_count=mock_count.return_value,
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_delegates_to_get_result_by_keys(self, mock_project, mock_get_result_by_keys):
        """get_result_by_keys receives the queryset, ids, and correct value_field."""
        project_ids = [10, 20]
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = [4, 8]

        result = await load_issues_count_by_project_id(project_ids)

        mock_get_result_by_keys.assert_called_once_with(
            mock_qs, project_ids, key_field="pk", value_field="items_count"
        )
        assert result == [4, 8]

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_zero_replaces_none(self, mock_project, mock_get_result_by_keys):
        """A None result is coerced to 0."""
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = [None]

        result = await load_issues_count_by_project_id([99])

        assert result == [0]

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_empty_project_ids(self, mock_project, mock_get_result_by_keys):
        """An empty project_ids list returns an empty list."""
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = []

        result = await load_issues_count_by_project_id([])

        assert result == []


class TestLoadRepositoriesCountByProjectId:
    """Tests for load_repositories_count_by_project_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_project, mock_get_result_by_keys):
        """Queryset is built with filter and annotate(Count)."""
        project_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = [0, 0, 0]

        await load_repositories_count_by_project_id(project_ids)

        mock_project.objects.filter.assert_called_once_with(pk__in=project_ids)
        mock_project.objects.filter.return_value.annotate.assert_called_once()

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_delegates_to_get_result_by_keys(self, mock_project, mock_get_result_by_keys):
        """get_result_by_keys receives the queryset, ids, and correct value_field."""
        project_ids = [10, 20]
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = [4, 8]

        result = await load_repositories_count_by_project_id(project_ids)

        mock_get_result_by_keys.assert_called_once_with(
            mock_qs, project_ids, key_field="pk", value_field="items_count"
        )
        assert result == [4, 8]

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_zero_replaces_none(self, mock_project, mock_get_result_by_keys):
        """A None result is coerced to 0."""
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = [None]

        result = await load_repositories_count_by_project_id([99])

        assert result == [0]

    @patch(
        "apps.owasp.api.internal.dataloaders.project.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.project.Project")
    @pytest.mark.asyncio
    async def test_empty_project_ids(self, mock_project, mock_get_result_by_keys):
        """An empty project_ids list returns an empty list."""
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = []

        result = await load_repositories_count_by_project_id([])

        assert result == []


class TestGetProjectLoaders:
    """Tests for get_project_loaders."""

    @pytest.mark.parametrize(
        "loader_key",
        [
            PROJECT_BY_REPOSITORY_ID_LOADER,
            HEALTH_METRICS_LIST_BY_PROJECT_ID,
            HEALTH_METRICS_LATEST_BY_PROJECT_ID,
            ISSUES_COUNT_BY_PROJECT_ID,
            OPEN_ISSUES_COUNT_BY_PROJECT_ID,
            REPOSITORIES_COUNT_BY_PROJECT_ID,
        ],
    )
    def test_returns_mapping(self, loader_key):
        """Factory always returns a Mapping."""
        loaders = get_project_loaders()
        assert loader_key in loaders
        assert isinstance(loaders[loader_key], DataLoader)

    def test_load_fn_is_load_projects_by_repository_id(self):
        """The project_by_repository_id loader is wired to load_projects_by_repository_id."""
        loaders = get_project_loaders()
        assert loaders[PROJECT_BY_REPOSITORY_ID_LOADER].load_fn is load_projects_by_repository_id

    def test_load_fn_is_load_health_metrics_list_by_project_id(self):
        """The list loader is wired to load_health_metrics_list_by_project_id."""
        loaders = get_project_loaders()
        assert (
            loaders[HEALTH_METRICS_LIST_BY_PROJECT_ID].load_fn
            is load_health_metrics_list_by_project_id
        )

    def test_load_fn_is_load_health_metrics_latest_by_project_id(self):
        """The latest loader is wired to load_health_metrics_latest_by_project_id."""
        loaders = get_project_loaders()
        assert (
            loaders[HEALTH_METRICS_LATEST_BY_PROJECT_ID].load_fn
            is load_health_metrics_latest_by_project_id
        )

    def test_load_fn_is_load_issues_count_by_project_id(self):
        """The issues count loader is wired to load_issues_count_by_project_id."""
        loaders = get_project_loaders()
        assert loaders[ISSUES_COUNT_BY_PROJECT_ID].load_fn is load_issues_count_by_project_id

    def test_load_fn_is_load_open_issues_count_by_project_id(self):
        """The open issues count loader is wired to load_open_issues_count_by_project_id."""
        loaders = get_project_loaders()
        assert (
            loaders[OPEN_ISSUES_COUNT_BY_PROJECT_ID].load_fn
            is load_open_issues_count_by_project_id
        )

    def test_load_fn_is_load_repositories_count_by_project_id(self):
        """The repositories count loader is wired to load_repositories_count_by_project_id."""
        loaders = get_project_loaders()
        assert (
            loaders[REPOSITORIES_COUNT_BY_PROJECT_ID].load_fn
            is load_repositories_count_by_project_id
        )

    @pytest.mark.parametrize(
        "loader_key",
        [
            PROJECT_BY_REPOSITORY_ID_LOADER,
            HEALTH_METRICS_LIST_BY_PROJECT_ID,
            HEALTH_METRICS_LATEST_BY_PROJECT_ID,
            ISSUES_COUNT_BY_PROJECT_ID,
            OPEN_ISSUES_COUNT_BY_PROJECT_ID,
            REPOSITORIES_COUNT_BY_PROJECT_ID,
        ],
    )
    def test_returns_new_instances_on_each_call(self, loader_key):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_project_loaders()
        loaders2 = get_project_loaders()
        assert loaders1 is not loaders2
        assert loaders1[loader_key] is not loaders2[loader_key]
