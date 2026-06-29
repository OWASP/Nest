"""Tests for project dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.owasp.api.internal.dataloaders.project import (
    PROJECT_BY_REPOSITORY_ID_LOADER,
    get_project_loaders,
    load_projects_by_repository_id,
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


class TestGetProjectLoaders:
    """Tests for get_project_loaders."""

    def test_returns_mapping(self):
        """Factory always returns a Mapping."""
        loaders = get_project_loaders()
        assert PROJECT_BY_REPOSITORY_ID_LOADER in loaders
        assert isinstance(loaders[PROJECT_BY_REPOSITORY_ID_LOADER], DataLoader)

    def test_load_fn_is_load_projects_by_repository_id(self):
        """The loader is wired to load_projects_by_repository_id."""
        loaders = get_project_loaders()
        loader = loaders[PROJECT_BY_REPOSITORY_ID_LOADER]
        assert loader.load_fn is load_projects_by_repository_id

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_project_loaders()
        loaders2 = get_project_loaders()
        assert loaders1 is not loaders2
        assert (
            loaders1[PROJECT_BY_REPOSITORY_ID_LOADER]
            is not loaders2[PROJECT_BY_REPOSITORY_ID_LOADER]
        )
