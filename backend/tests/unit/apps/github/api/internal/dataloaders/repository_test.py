"""Tests for repository dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.repository import (
    RELEASE_URL_BY_ID_LOADER,
    REPOSITORY_BY_RELEASE_ID_LOADER,
    get_repository_loaders,
    load_release_urls_by_id,
    load_repositories_by_release_id,
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


class TestLoadReleaseUrlsById:
    """Tests for load_release_urls_by_id."""

    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_release):
        """Queryset is built with filter and select_related in the right order."""
        mock_queryset = MagicMock()
        mock_release.objects.filter.return_value.select_related.return_value = mock_queryset
        mock_queryset.__aiter__.return_value = iter([])

        await load_release_urls_by_id([1, 2])

        mock_release.objects.filter.assert_called_once_with(pk__in=[1, 2])
        mock_release.objects.filter.return_value.select_related.assert_called_once_with(
            "repository__owner", "repository__organization"
        )

    @patch("apps.github.api.internal.dataloaders.repository.Release")
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

    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_empty_repository_returns_empty_string(self, mock_release):
        """A release with no repository yields an empty string."""
        release = MagicMock(pk=1, repository=None, tag_name="v1.0")
        mock_qs = mock_release.objects.filter.return_value.select_related.return_value
        mock_qs.__aiter__.return_value = iter([release])

        result = await load_release_urls_by_id([1])

        assert result == [""]

    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_missing_release_id_returns_empty_string(self, mock_release):
        """A release ID not found in the queryset yields an empty string."""
        mock_qs = mock_release.objects.filter.return_value.select_related.return_value
        mock_qs.__aiter__.return_value = iter([])

        result = await load_release_urls_by_id([99])

        assert result == [""]

    @patch("apps.github.api.internal.dataloaders.repository.Release")
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

    @patch("apps.github.api.internal.dataloaders.repository.Release")
    @pytest.mark.asyncio
    async def test_empty_release_ids(self, mock_release):
        """An empty release_ids list returns an empty list."""
        mock_qs = mock_release.objects.filter.return_value.select_related.return_value
        mock_qs.__aiter__.return_value = iter([])

        result = await load_release_urls_by_id([])

        assert result == []


class TestGetRepositoryLoaders:
    """Tests for get_repository_loaders."""

    def test_returns_mapping_with_both_loaders(self):
        """Factory returns a mapping with both expected loaders."""
        loaders = get_repository_loaders()
        assert REPOSITORY_BY_RELEASE_ID_LOADER in loaders
        assert RELEASE_URL_BY_ID_LOADER in loaders
        assert isinstance(loaders[REPOSITORY_BY_RELEASE_ID_LOADER], DataLoader)
        assert isinstance(loaders[RELEASE_URL_BY_ID_LOADER], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_repository_loaders()
        loaders2 = get_repository_loaders()
        assert loaders1 is not loaders2
        assert (
            loaders1[REPOSITORY_BY_RELEASE_ID_LOADER]
            is not loaders2[REPOSITORY_BY_RELEASE_ID_LOADER]
        )
        assert loaders1[RELEASE_URL_BY_ID_LOADER] is not loaders2[RELEASE_URL_BY_ID_LOADER]

    def test_load_fn_is_load_repositories_by_release_id(self):
        """The repository loader is wired to load_repositories_by_release_id."""
        loaders = get_repository_loaders()
        loader = loaders[REPOSITORY_BY_RELEASE_ID_LOADER]
        assert loader.load_fn is load_repositories_by_release_id

    def test_load_fn_is_load_release_urls_by_id(self):
        """The URL loader is wired to load_release_urls_by_id."""
        loaders = get_repository_loaders()
        loader = loaders[RELEASE_URL_BY_ID_LOADER]
        assert loader.load_fn is load_release_urls_by_id
