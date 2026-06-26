"""Tests for release dataloaders."""

from unittest.mock import MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.release import (
    RELEASE_URL_BY_ID_LOADER,
    get_release_loaders,
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


class TestGetReleaseLoaders:
    """Tests for get_release_loaders."""

    def test_returns_mapping_with_release_url_loader(self):
        """Factory returns a mapping with the release URL loader."""
        loaders = get_release_loaders()
        assert RELEASE_URL_BY_ID_LOADER in loaders
        assert isinstance(loaders[RELEASE_URL_BY_ID_LOADER], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_release_loaders()
        loaders2 = get_release_loaders()
        assert loaders1 is not loaders2
        assert loaders1[RELEASE_URL_BY_ID_LOADER] is not loaders2[RELEASE_URL_BY_ID_LOADER]

    def test_load_fn_is_load_release_urls_by_id(self):
        """The URL loader is wired to load_release_urls_by_id."""
        loaders = get_release_loaders()
        loader = loaders[RELEASE_URL_BY_ID_LOADER]
        assert loader.load_fn is load_release_urls_by_id
