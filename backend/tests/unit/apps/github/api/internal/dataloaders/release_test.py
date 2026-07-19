"""Tests for release dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.release import (
    LATEST_RELEASE_BY_REPOSITORY_ID_LOADER,
    RECENT_RELEASES_BY_PROJECT_ID,
    RECENT_RELEASES_BY_REPOSITORY_ID_LOADER,
    RELEASE_URL_BY_ID_LOADER,
    get_release_loaders,
    load_latest_releases_by_repository_id,
    load_recent_releases_by_project_id,
    load_recent_releases_by_repository_id,
    load_release_urls_by_id,
)


class TestLoadReleaseUrlsById:
    """Tests for load_release_urls_by_id."""

    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_release):
        """Queryset is built with filter and select_related in the right order."""
        mock_queryset = MagicMock()
        mock_release.objects.filter.return_value.select_related.return_value = mock_queryset
        mock_queryset.__aiter__.return_value = iter([])

        await load_release_urls_by_id([1, 2])

        mock_release.objects.filter.assert_called_once_with(pk__in=[1, 2])
        mock_release.objects.filter.return_value.select_related.assert_called_once_with(
            "repository__owner"
        )

    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_constructs_url_correctly(self, mock_release):
        """Each release's URL is built from repository.url and tag_name."""
        mock_repo_1 = MagicMock()
        mock_repo_1.url = "https://github.com/owner-a/repo-a"
        mock_repo_2 = MagicMock()
        mock_repo_2.url = "https://github.com/owner-b/repo-b"

        release_1 = MagicMock(pk=1, repository=mock_repo_1, tag_name="v1.0")
        release_2 = MagicMock(pk=2, repository=mock_repo_2, tag_name="v2.0")

        mock_qs = mock_release.objects.filter.return_value.select_related.return_value
        mock_qs.__aiter__.return_value = iter([release_1, release_2])

        result = await load_release_urls_by_id([1, 2])

        assert result == [
            "https://github.com/owner-a/repo-a/releases/tag/v1.0",
            "https://github.com/owner-b/repo-b/releases/tag/v2.0",
        ]

    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_empty_repository_returns_empty_string(self, mock_release):
        """A release with no repository yields an empty string."""
        release = MagicMock(pk=1, repository=None, tag_name="v1.0")
        mock_qs = mock_release.objects.filter.return_value.select_related.return_value
        mock_qs.__aiter__.return_value = iter([release])

        result = await load_release_urls_by_id([1])

        assert result == [""]

    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_missing_release_id_returns_empty_string(self, mock_release):
        """A release ID not found in the queryset yields an empty string."""
        mock_qs = mock_release.objects.filter.return_value.select_related.return_value
        mock_qs.__aiter__.return_value = iter([])

        result = await load_release_urls_by_id([99])

        assert result == [""]

    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_order_matches_keys_not_queryset(self, mock_release):
        """The output order follows release_ids, not the queryset iteration order."""
        mock_repo = MagicMock()
        mock_repo.url = "https://github.com/owner/repo"

        release_2 = MagicMock(pk=2, repository=mock_repo, tag_name="v2.0")
        release_1 = MagicMock(pk=1, repository=mock_repo, tag_name="v1.0")

        mock_qs = mock_release.objects.filter.return_value.select_related.return_value
        mock_qs.__aiter__.return_value = iter([release_2, release_1])

        result = await load_release_urls_by_id([1, 2])

        assert result == [
            "https://github.com/owner/repo/releases/tag/v1.0",
            "https://github.com/owner/repo/releases/tag/v2.0",
        ]

    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_empty_release_ids(self, mock_release):
        """An empty release_ids list returns an empty list."""
        mock_qs = mock_release.objects.filter.return_value.select_related.return_value
        mock_qs.__aiter__.return_value = iter([])

        result = await load_release_urls_by_id([])

        assert result == []


class TestLoadLatestReleasesByRepositoryId:
    """Tests for load_latest_releases_by_repository_id."""

    @patch(
        "apps.github.api.internal.dataloaders.release.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_release, mock_get_result_by_keys):
        """Queryset is built with filter, distinct, select_related, order_by, only."""
        repository_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_filter = mock_release.objects.filter.return_value
        mock_distinct = mock_filter.distinct.return_value
        mock_sel = mock_distinct.select_related.return_value
        mock_chain = mock_sel.order_by.return_value
        mock_chain.only.return_value = mock_qs
        mock_get_result_by_keys.return_value = [None, None, None]

        await load_latest_releases_by_repository_id(repository_ids)

        mock_release.objects.filter.assert_called_once_with(
            repository_id__in=repository_ids,
            is_draft=False,
            is_pre_release=False,
            published_at__isnull=False,
        )
        mock_filter.distinct.assert_called_once_with("repository_id")
        mock_distinct.select_related.assert_called_once_with("author")
        mock_sel.order_by.assert_called_once_with("repository_id", "-published_at")
        mock_chain.only.assert_called_once_with(
            "repository_id", "author__login", "author__name", "name"
        )

    @patch(
        "apps.github.api.internal.dataloaders.release.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_delegates_to_get_result_by_keys(self, mock_release, mock_get_result_by_keys):
        """get_result_by_keys receives the queryset, ids, and correct key_field."""
        repository_ids = [10, 20]
        mock_qs = MagicMock()
        mock_filter = mock_release.objects.filter.return_value
        mock_distinct = mock_filter.distinct.return_value
        mock_sel = mock_distinct.select_related.return_value
        mock_chain = mock_sel.order_by.return_value
        mock_chain.only.return_value = mock_qs
        mock_get_result_by_keys.return_value = [None, None]

        await load_latest_releases_by_repository_id(repository_ids)

        mock_get_result_by_keys.assert_called_once_with(
            mock_qs, repository_ids, key_field="repository_id"
        )

    @patch(
        "apps.github.api.internal.dataloaders.release.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_returns_none_when_no_release(self, mock_release, mock_get_result_by_keys):
        """A repository with no matching release gets None."""
        mock_qs = MagicMock()
        mock_filter = mock_release.objects.filter.return_value
        mock_distinct = mock_filter.distinct.return_value
        mock_sel = mock_distinct.select_related.return_value
        mock_chain = mock_sel.order_by.return_value
        mock_chain.only.return_value = mock_qs
        mock_get_result_by_keys.return_value = [None]

        result = await load_latest_releases_by_repository_id([99])

        assert result == [None]

    @patch(
        "apps.github.api.internal.dataloaders.release.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_empty_repository_ids(self, mock_release, mock_get_result_by_keys):
        """An empty repository_ids list returns an empty list."""
        mock_qs = MagicMock()
        mock_filter = mock_release.objects.filter.return_value
        mock_distinct = mock_filter.distinct.return_value
        mock_sel = mock_distinct.select_related.return_value
        mock_chain = mock_sel.order_by.return_value
        mock_chain.only.return_value = mock_qs
        mock_get_result_by_keys.return_value = []

        result = await load_latest_releases_by_repository_id([])

        assert result == []


class TestLoadRecentReleasesByRepositoryId:
    """Tests for load_recent_releases_by_repository_id."""

    @patch(
        "apps.github.api.internal.dataloaders.release.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_release, mock_get_results_by_keys
    ):
        """Queryset is built with filter, annotate, and order_by."""
        keys = [(1, 5), (2, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_release.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], []]

        await load_recent_releases_by_repository_id(keys)

        mock_release.objects.filter.assert_called_once_with(
            repository_id__in=[1, 2],
            is_draft=False,
            is_pre_release=False,
            published_at__isnull=False,
        )
        mock_filter.annotate.assert_called_once()
        mock_filter.annotate.return_value.filter.assert_called_once_with(row_number__lte=5)
        mock_filter.annotate.return_value.filter.return_value.order_by.assert_called_once_with(
            "repository_id", "-published_at"
        )

    @patch(
        "apps.github.api.internal.dataloaders.release.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys(self, mock_release, mock_get_results_by_keys):
        """get_results_by_keys receives the queryset, ids, and correct key_field."""
        keys = [(10, 5), (20, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_release.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], []]

        await load_recent_releases_by_repository_id(keys)

        mock_get_results_by_keys.assert_called_once_with(
            mock_qs, [10, 20], key_field="repository_id"
        )

    @patch(
        "apps.github.api.internal.dataloaders.release.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_empty_keys(self, mock_release, mock_get_results_by_keys):
        """An empty keys list returns an empty list."""
        mock_get_results_by_keys.return_value = []

        result = await load_recent_releases_by_repository_id([])

        assert result == []

    @patch(
        "apps.github.api.internal.dataloaders.release.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_window_filter_enforces_limit(self, mock_release, mock_get_results_by_keys):
        """The window function filter enforces the limit."""
        keys = [(1, 3)]
        mock_qs = MagicMock()
        mock_filter = mock_release.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[MagicMock(), MagicMock(), MagicMock()]]

        result = await load_recent_releases_by_repository_id(keys)

        mock_filter.annotate.return_value.filter.assert_called_once_with(row_number__lte=3)
        assert len(result[0]) == 3

    @patch(
        "apps.github.api.internal.dataloaders.release.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_release, mock_get_results_by_keys
    ):
        """The return value is what get_results_by_keys resolves to."""
        keys = [(1, 5)]
        mock_qs = MagicMock()
        mock_filter = mock_release.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = mock_qs
        mock_release_obj = MagicMock()
        expected = [[mock_release_obj]]
        mock_get_results_by_keys.return_value = expected

        result = await load_recent_releases_by_repository_id(keys)

        assert result == expected


class TestLoadRecentReleasesByProjectId:
    """Tests for load_recent_releases_by_project_id."""

    @staticmethod
    def _ordered_qs(mock_release):
        """Return the mock queryset at the end of the releases chain."""
        call = mock_release.objects.filter.return_value
        return call.prefetch_related.return_value.order_by.return_value

    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_release):
        """Queryset is built with filter, prefetch_related, order_by, distinct."""
        mock_filter_result = mock_release.objects.filter.return_value
        mock_ordered = self._ordered_qs(mock_release)
        mock_ordered.distinct.return_value = MagicMock()
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([])

        await load_recent_releases_by_project_id([(1, 5), (2, 5)])

        mock_release.objects.filter.assert_called_once_with(
            is_draft=False,
            is_pre_release=False,
            published_at__isnull=False,
            repository__project__in=[1, 2],
        )
        mock_filter_result.prefetch_related.assert_called_once()
        mock_filter_result.prefetch_related.return_value.order_by.assert_called_once_with(
            "-published_at"
        )
        mock_ordered.distinct.assert_called_once()

    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_maps_releases_to_project_ids(self, mock_release):
        """Releases are mapped to the projects that own the release's repository."""
        project_1 = MagicMock(pk=1)
        project_2 = MagicMock(pk=2)
        release_a = MagicMock()
        release_a.repository.prefetched_projects = [project_1]
        release_b = MagicMock()
        release_b.repository.prefetched_projects = [project_2]

        mock_ordered = self._ordered_qs(mock_release)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([release_a, release_b])

        result = await load_recent_releases_by_project_id([(1, 5), (2, 5)])

        assert result == [[release_a], [release_b]]

    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_limit_enforced_per_project(self, mock_release):
        """Each project list is truncated to the configured limit."""
        project = MagicMock(pk=1)
        releases = [MagicMock() for _ in range(5)]
        for release in releases:
            release.repository.prefetched_projects = [project]

        mock_ordered = self._ordered_qs(mock_release)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter(releases)

        result = await load_recent_releases_by_project_id([(1, 3)])

        assert result == [[releases[0], releases[1], releases[2]]]

    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_order_matches_keys_not_queryset(self, mock_release):
        """The output order follows project_ids, not the queryset iteration order."""
        project_1 = MagicMock(pk=1)
        project_2 = MagicMock(pk=2)
        release_b = MagicMock()
        release_b.repository.prefetched_projects = [project_2]
        release_a = MagicMock()
        release_a.repository.prefetched_projects = [project_1]

        mock_ordered = self._ordered_qs(mock_release)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([release_b, release_a])

        result = await load_recent_releases_by_project_id([(1, 5), (2, 5)])

        assert result == [[release_a], [release_b]]

    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_shared_repository_appears_in_each_project(self, mock_release):
        """A repo shared between projects contributes the release to each project."""
        project_1 = MagicMock(pk=1)
        project_2 = MagicMock(pk=2)
        release = MagicMock()
        release.repository.prefetched_projects = [project_1, project_2]

        mock_ordered = self._ordered_qs(mock_release)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([release])

        result = await load_recent_releases_by_project_id([(1, 5), (2, 5)])

        assert result == [[release], [release]]

    @pytest.mark.asyncio
    async def test_empty_keys(self):
        """An empty keys list returns an empty list."""
        result = await load_recent_releases_by_project_id([])
        assert result == []

    @patch("apps.github.api.internal.dataloaders.release.Release")
    @pytest.mark.asyncio
    async def test_missing_project_returns_empty_list(self, mock_release):
        """A project ID with no matching releases gets an empty list."""
        mock_ordered = self._ordered_qs(mock_release)
        mock_ordered.distinct.return_value.__aiter__.return_value = iter([])

        result = await load_recent_releases_by_project_id([(99, 5)])

        assert result == [[]]


class TestGetReleaseLoaders:
    """Tests for get_release_loaders."""

    def test_returns_mapping_with_all_loaders(self):
        """Factory returns a mapping with all loader keys."""
        loaders = get_release_loaders()
        for key in [
            RELEASE_URL_BY_ID_LOADER,
            LATEST_RELEASE_BY_REPOSITORY_ID_LOADER,
            RECENT_RELEASES_BY_REPOSITORY_ID_LOADER,
            RECENT_RELEASES_BY_PROJECT_ID,
        ]:
            assert key in loaders
            assert isinstance(loaders[key], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_release_loaders()
        loaders2 = get_release_loaders()
        assert loaders1 is not loaders2
        for key in [
            RELEASE_URL_BY_ID_LOADER,
            LATEST_RELEASE_BY_REPOSITORY_ID_LOADER,
            RECENT_RELEASES_BY_REPOSITORY_ID_LOADER,
            RECENT_RELEASES_BY_PROJECT_ID,
        ]:
            assert loaders1[key] is not loaders2[key]

    def test_load_fn_is_load_release_urls_by_id(self):
        """The URL loader is wired to load_release_urls_by_id."""
        loaders = get_release_loaders()
        loader = loaders[RELEASE_URL_BY_ID_LOADER]
        assert loader.load_fn is load_release_urls_by_id

    def test_load_fn_is_load_latest_releases_by_repository_id(self):
        """The latest release loader is wired to load_latest_releases_by_repository_id."""
        loaders = get_release_loaders()
        loader = loaders[LATEST_RELEASE_BY_REPOSITORY_ID_LOADER]
        assert loader.load_fn is load_latest_releases_by_repository_id

    def test_load_fn_is_load_recent_releases_by_repository_id(self):
        """The recent releases loader is wired to load_recent_releases_by_repository_id."""
        loaders = get_release_loaders()
        loader = loaders[RECENT_RELEASES_BY_REPOSITORY_ID_LOADER]
        assert loader.load_fn is load_recent_releases_by_repository_id

    def test_load_fn_is_load_recent_releases_by_project_id(self):
        """The project releases loader is wired to load_recent_releases_by_project_id."""
        loaders = get_release_loaders()
        loader = loaders[RECENT_RELEASES_BY_PROJECT_ID]
        assert loader.load_fn is load_recent_releases_by_project_id
