"""Tests for repository dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.repository import (
    REPOSITORIES_BY_PROJECT_ID,
    REPOSITORIES_COUNT_BY_PROJECT_ID,
    REPOSITORY_BY_RELEASE_ID_LOADER,
    REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER,
    get_repository_loaders,
    load_repositories_by_project_id,
    load_repositories_by_release_id,
    load_repositories_count_by_project_id,
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


class TestLoadRepositoriesByProjectId:
    """Tests for load_repositories_by_project_id."""

    @staticmethod
    def _ordered_qs(mock_repository):
        """Return the mock queryset at the end of the repositories chain."""
        call = mock_repository.objects.filter.return_value
        return call.prefetch_related.return_value.order_by.return_value

    @patch("apps.github.api.internal.dataloaders.repository.Repository")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_repository):
        """Queryset filters by project + organization, orders by pushed/updated, distincts."""
        mock_filter_result = mock_repository.objects.filter.return_value
        mock_ordered = self._ordered_qs(mock_repository)
        mock_ordered.distinct.return_value = MagicMock()
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([])

        await load_repositories_by_project_id([1, 2])

        mock_repository.objects.filter.assert_called_once_with(
            project__in=[1, 2], organization__isnull=False
        )
        mock_filter_result.prefetch_related.assert_called_once()
        mock_filter_result.prefetch_related.return_value.order_by.assert_called_once_with(
            "-pushed_at", "-updated_at"
        )
        mock_ordered.distinct.assert_called_once()

    @patch("apps.github.api.internal.dataloaders.repository.Repository")
    @pytest.mark.asyncio
    async def test_maps_repositories_to_project_ids(self, mock_repository):
        """Repositories are mapped to the projects they belong to."""
        project_1 = MagicMock(pk=1)
        project_2 = MagicMock(pk=2)
        repo_a = MagicMock()
        repo_a.prefetched_projects = [project_1]
        repo_b = MagicMock()
        repo_b.prefetched_projects = [project_2]

        mock_ordered = self._ordered_qs(mock_repository)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([repo_a, repo_b])

        result = await load_repositories_by_project_id([1, 2])

        assert result == [[repo_a], [repo_b]]

    @patch("apps.github.api.internal.dataloaders.repository.Repository")
    @pytest.mark.asyncio
    async def test_shared_repository_appears_in_each_project(self, mock_repository):
        """A repo shared between projects is returned for each project."""
        project_1 = MagicMock(pk=1)
        project_2 = MagicMock(pk=2)
        repo = MagicMock()
        repo.prefetched_projects = [project_1, project_2]

        mock_ordered = self._ordered_qs(mock_repository)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([repo])

        result = await load_repositories_by_project_id([1, 2])

        assert result == [[repo], [repo]]

    @patch("apps.github.api.internal.dataloaders.repository.Repository")
    @pytest.mark.asyncio
    async def test_order_matches_keys_not_queryset(self, mock_repository):
        """The output order follows project_ids, not the queryset iteration order."""
        project_1 = MagicMock(pk=1)
        project_2 = MagicMock(pk=2)
        repo_b = MagicMock()
        repo_b.prefetched_projects = [project_2]
        repo_a = MagicMock()
        repo_a.prefetched_projects = [project_1]

        mock_ordered = self._ordered_qs(mock_repository)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([repo_b, repo_a])

        result = await load_repositories_by_project_id([1, 2])

        assert result == [[repo_a], [repo_b]]

    @pytest.mark.asyncio
    async def test_empty_project_ids(self):
        """An empty project_ids list returns an empty list."""
        result = await load_repositories_by_project_id([])
        assert result == []

    @patch("apps.github.api.internal.dataloaders.repository.Repository")
    @pytest.mark.asyncio
    async def test_missing_project_returns_empty_list(self, mock_repository):
        """A project ID with no matching repositories gets an empty list."""
        mock_ordered = self._ordered_qs(mock_repository)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([])

        result = await load_repositories_by_project_id([99])

        assert result == [[]]


class TestLoadRepositoriesCountByProjectId:
    """Tests for load_repositories_count_by_project_id."""

    @patch(
        "apps.github.api.internal.dataloaders.repository.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.repository.Repository")
    @patch("apps.github.api.internal.dataloaders.repository.Project")
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

        await load_repositories_count_by_project_id(project_ids)

        mock_repository.objects.filter.assert_called_once_with(organization__isnull=False)
        mock_project.objects.filter.assert_called_once_with(
            pk__in=project_ids, repositories__in=mock_subq
        )
        mock_project.objects.filter.return_value.annotate.assert_called_once()

    @patch(
        "apps.github.api.internal.dataloaders.repository.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.repository.Repository")
    @patch("apps.github.api.internal.dataloaders.repository.Project")
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

        result = await load_repositories_count_by_project_id(project_ids)

        mock_get_result_by_keys.assert_called_once_with(
            mock_qs, project_ids, key_field="pk", value_field="items_count"
        )
        assert result == [4, 8]

    @patch(
        "apps.github.api.internal.dataloaders.repository.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.repository.Repository")
    @patch("apps.github.api.internal.dataloaders.repository.Project")
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

        result = await load_repositories_count_by_project_id([99])

        assert result == [0]

    @patch(
        "apps.github.api.internal.dataloaders.repository.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.repository.Repository")
    @patch("apps.github.api.internal.dataloaders.repository.Project")
    @pytest.mark.asyncio
    async def test_empty_project_ids(self, mock_project, mock_repository, mock_get_result_by_keys):
        """An empty project_ids list returns an empty list."""
        mock_subq = MagicMock()
        mock_repository.objects.filter.return_value = mock_subq
        mock_qs = MagicMock()
        mock_project.objects.filter.return_value.annotate.return_value = mock_qs
        mock_get_result_by_keys.return_value = []

        result = await load_repositories_count_by_project_id([])

        assert result == []


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

    def test_returns_mapping_with_repositories_by_project_loader(self):
        """Factory returns a mapping with the repositories-by-project loader."""
        loaders = get_repository_loaders()
        assert REPOSITORIES_BY_PROJECT_ID in loaders
        assert isinstance(loaders[REPOSITORIES_BY_PROJECT_ID], DataLoader)

    def test_repositories_by_project_loader_is_distinct_instance(self):
        """Each call produces distinct DataLoader instances."""
        loaders1 = get_repository_loaders()
        loaders2 = get_repository_loaders()
        assert loaders1[REPOSITORIES_BY_PROJECT_ID] is not loaders2[REPOSITORIES_BY_PROJECT_ID]

    def test_load_fn_is_load_repositories_by_project_id(self):
        """The repositories-by-project loader is wired to load_repositories_by_project_id."""
        loaders = get_repository_loaders()
        loader = loaders[REPOSITORIES_BY_PROJECT_ID]
        assert loader.load_fn is load_repositories_by_project_id

    def test_returns_mapping_with_repositories_count_loader(self):
        """Factory returns a mapping with the repositories count loader."""
        loaders = get_repository_loaders()
        assert REPOSITORIES_COUNT_BY_PROJECT_ID in loaders
        assert isinstance(loaders[REPOSITORIES_COUNT_BY_PROJECT_ID], DataLoader)

    def test_repositories_count_loader_is_distinct_instance(self):
        """Each call produces distinct DataLoader instances."""
        loaders1 = get_repository_loaders()
        loaders2 = get_repository_loaders()
        assert (
            loaders1[REPOSITORIES_COUNT_BY_PROJECT_ID]
            is not loaders2[REPOSITORIES_COUNT_BY_PROJECT_ID]
        )

    def test_load_fn_is_load_repositories_count_by_project_id(self):
        """The repositories count loader is wired to load_repositories_count_by_project_id."""
        loaders = get_repository_loaders()
        assert (
            loaders[REPOSITORIES_COUNT_BY_PROJECT_ID].load_fn
            is load_repositories_count_by_project_id
        )
