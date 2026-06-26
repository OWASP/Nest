"""Tests for repository dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.repository import (
    REPOSITORY_BY_RELEASE_ID_LOADER,
    REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER,
    get_repository_loaders,
    load_repositories_by_release_id,
    load_repository_project_names_by_release_id,
)


class TestLoadRepositoriesByReleaseId:
    """Tests for load_repositories_by_release_id."""

    @patch(
        "apps.github.api.internal.dataloaders.repository.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_release, mock_get_result_by_keys):
        """Queryset is built with filter and select_related in the right order."""
        release_ids = [1, 2, 3]
        mock_queryset = MagicMock()
        mock_release.objects.filter.return_value.select_related.return_value = mock_queryset
        mock_get_result_by_keys.return_value = [None, None, None]

        await load_repositories_by_release_id(release_ids)

        mock_release.objects.filter.assert_called_once_with(pk__in=release_ids)
        mock_release.objects.filter.return_value.select_related.assert_called_once_with(
            "repository__organization", "repository__owner"
        )

    @patch(
        "apps.github.api.internal.dataloaders.repository.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_delegates_to_get_result_by_keys_correct_args(
        self, mock_release, mock_get_result_by_keys
    ):
        """get_result_by_keys receives the queryset, release_ids, and correct field names."""
        release_ids = [10, 20]
        mock_queryset = MagicMock()
        mock_release.objects.filter.return_value.select_related.return_value = mock_queryset
        mock_get_result_by_keys.return_value = [None, None]

        await load_repositories_by_release_id(release_ids)

        mock_get_result_by_keys.assert_called_once_with(
            mock_queryset, release_ids, key_field="pk", value_field="repository"
        )

    @patch(
        "apps.github.api.internal.dataloaders.repository.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_result_by_keys(
        self, mock_release, mock_get_result_by_keys
    ):
        """The return value is exactly what get_result_by_keys resolves to."""
        mock_repo = MagicMock()
        expected = [mock_repo, None]
        mock_release.objects.filter.return_value.select_related.return_value = MagicMock()
        mock_get_result_by_keys.return_value = expected

        result = await load_repositories_by_release_id([1, 2])

        assert result is expected

    @patch(
        "apps.github.api.internal.dataloaders.repository.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_empty_release_ids(self, mock_release, mock_get_result_by_keys):
        """An empty release_ids list results in an empty filter and empty return."""
        mock_release.objects.filter.return_value.select_related.return_value = MagicMock()
        mock_get_result_by_keys.return_value = []

        result = await load_repositories_by_release_id([])

        mock_release.objects.filter.assert_called_once_with(pk__in=[])
        assert result == []

    @patch(
        "apps.github.api.internal.dataloaders.repository.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_single_release_id(self, mock_release, mock_get_result_by_keys):
        """A single-element list is handled correctly end-to-end."""
        mock_repo = MagicMock()
        mock_release.objects.filter.return_value.select_related.return_value = MagicMock()
        mock_get_result_by_keys.return_value = [mock_repo]

        result = await load_repositories_by_release_id([42])

        mock_release.objects.filter.assert_called_once_with(pk__in=[42])
        assert result == [mock_repo]


class TestLoadRepositoryProjectNamesByReleaseId:
    """Tests for load_repository_project_names_by_release_id."""

    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_release):
        """Queryset uses filter, select_related, and prefetch_related."""
        release_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_release.objects.filter.return_value = mock_qs
        mock_qs.select_related.return_value = mock_qs
        mock_qs.prefetch_related.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter([])

        await load_repository_project_names_by_release_id(release_ids)

        mock_release.objects.filter.assert_called_once_with(pk__in=release_ids)
        mock_qs.select_related.assert_called_once_with("repository")
        mock_qs.prefetch_related.assert_called_once()

    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_maps_release_ids_to_project_names(self, mock_release):
        """Returns project names in order of release_ids."""
        release_ids = [1, 2, 3]
        project_1 = MagicMock()
        project_1.name = "Project Alpha"
        project_2 = MagicMock()
        project_2.name = "Project Beta"
        releases = [
            MagicMock(pk=1, repository=MagicMock(prefetched_projects=[project_1])),
            MagicMock(pk=2, repository=MagicMock(prefetched_projects=[project_2])),
            MagicMock(pk=3, repository=None),
        ]
        mock_qs = MagicMock()
        mock_release.objects.filter.return_value = mock_qs
        mock_qs.select_related.return_value = mock_qs
        mock_qs.prefetch_related.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter(releases)

        result = await load_repository_project_names_by_release_id(release_ids)

        assert result == ["Project Alpha", "Project Beta", None]

    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_empty_release_ids(self, mock_release):
        """An empty release_ids list returns an empty list."""
        mock_qs = MagicMock()
        mock_release.objects.filter.return_value = mock_qs
        mock_qs.select_related.return_value = mock_qs
        mock_qs.prefetch_related.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter([])

        result = await load_repository_project_names_by_release_id([])

        assert result == []

    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_release_without_repository_returns_none(self, mock_release):
        """A release with no repository maps to None."""
        release_ids = [1]
        releases = [MagicMock(pk=1, repository=None)]
        mock_qs = MagicMock()
        mock_release.objects.filter.return_value = mock_qs
        mock_qs.select_related.return_value = mock_qs
        mock_qs.prefetch_related.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter(releases)

        result = await load_repository_project_names_by_release_id(release_ids)

        assert result == [None]

    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_release_without_projects_returns_none(self, mock_release):
        """A release with a repository but no prefetched projects maps to None."""
        release_ids = [1]
        releases = [MagicMock(pk=1, repository=MagicMock(prefetched_projects=[]))]
        mock_qs = MagicMock()
        mock_release.objects.filter.return_value = mock_qs
        mock_qs.select_related.return_value = mock_qs
        mock_qs.prefetch_related.return_value = qs = MagicMock()
        qs.__aiter__.return_value = iter(releases)

        result = await load_repository_project_names_by_release_id(release_ids)

        assert result == [None]


class TestGetRepositoryLoaders:
    """Tests for get_repository_loaders."""

    def test_returns_mapping_with_repository_loader(self):
        """Factory returns a mapping with the repository loader."""
        loaders = get_repository_loaders()
        assert REPOSITORY_BY_RELEASE_ID_LOADER in loaders
        assert isinstance(loaders[REPOSITORY_BY_RELEASE_ID_LOADER], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_repository_loaders()
        loaders2 = get_repository_loaders()
        assert loaders1 is not loaders2
        assert (
            loaders1[REPOSITORY_BY_RELEASE_ID_LOADER]
            is not loaders2[REPOSITORY_BY_RELEASE_ID_LOADER]
        )

    def test_load_fn_is_load_repositories_by_release_id(self):
        """The repository loader is wired to load_repositories_by_release_id."""
        loaders = get_repository_loaders()
        loader = loaders[REPOSITORY_BY_RELEASE_ID_LOADER]
        assert loader.load_fn is load_repositories_by_release_id

    def test_returns_mapping_with_project_name_loader(self):
        """Factory returns a mapping with the project name loader."""
        loaders = get_repository_loaders()
        assert REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER in loaders
        assert isinstance(loaders[REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER], DataLoader)

    def test_project_name_loader_is_distinct_instance(self):
        """Each call produces distinct DataLoader instances."""
        loaders1 = get_repository_loaders()
        loaders2 = get_repository_loaders()
        assert (
            loaders1[REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER]
            is not loaders2[REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER]
        )

    def test_load_fn_is_load_repository_project_names_by_release_id(self):
        """The project name loader is wired to the correct function."""
        loaders = get_repository_loaders()
        loader = loaders[REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER]
        assert loader.load_fn is load_repository_project_names_by_release_id
