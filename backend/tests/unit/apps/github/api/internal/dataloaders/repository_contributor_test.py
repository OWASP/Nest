"""Tests for repository contributor dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.repository_contributor import (
    TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER,
    TOP_CONTRIBUTORS_LIMIT,
    get_repository_contributor_loaders,
    load_top_contributors_by_repository_id,
)


class TestLoadTopContributorsByRepositoryId:
    """Tests for load_top_contributors_by_repository_id."""

    @staticmethod
    def _setup_sync_to_async(mock_sync_to_async, mock_qs):
        """Configure sync_to_async mock: returns a callable that returns an awaitable."""
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_qs)

    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.get_top_contributors_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.sync_to_async",
    )
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_sync_to_async, mock_get_top_contributors
    ):
        """Queryset is built with filter, annotate (window), filter (row_number), order_by."""
        repository_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_filter_result = mock_qs.filter.return_value
        mock_annotate_result = mock_filter_result.annotate.return_value
        mock_annotate_result.filter.return_value.order_by.return_value = mock_qs
        self._setup_sync_to_async(mock_sync_to_async, mock_qs)
        mock_get_top_contributors.return_value = [[], [], []]

        await load_top_contributors_by_repository_id(repository_ids)

        mock_qs.filter.assert_called_once_with(repository_id__in=repository_ids)
        mock_filter_result.annotate.assert_called_once()
        mock_annotate_result.filter.assert_called_once()

    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.get_top_contributors_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.sync_to_async",
    )
    @pytest.mark.asyncio
    async def test_delegates_to_get_top_contributors_by_keys(
        self, mock_sync_to_async, mock_get_top_contributors
    ):
        """Delegates to get_top_contributors_by_keys with correct args."""
        repository_ids = [10, 20]
        mock_qs = MagicMock()
        mock_chain = mock_qs.filter.return_value.annotate.return_value.filter.return_value
        mock_order_by = mock_chain.order_by.return_value
        self._setup_sync_to_async(mock_sync_to_async, mock_qs)
        mock_get_top_contributors.return_value = [[], []]

        await load_top_contributors_by_repository_id(repository_ids)

        mock_get_top_contributors.assert_called_once_with(
            queryset=mock_order_by, keys=repository_ids, key_field="repository_id"
        )

    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.get_top_contributors_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.sync_to_async",
    )
    @pytest.mark.asyncio
    async def test_returns_result_from_get_top_contributors(
        self, mock_sync_to_async, mock_get_top_contributors
    ):
        """Return value is exactly what get_top_contributors_by_keys resolves to."""
        repository_ids = [1, 2]
        mock_qs = MagicMock()
        self._setup_sync_to_async(mock_sync_to_async, mock_qs)
        expected = [
            [
                {
                    "avatar_url": "url1",
                    "contributions_count": 100,
                    "id": "user1",
                    "login": "user1",
                    "name": "User 1",
                }
            ],
            [
                {
                    "avatar_url": "url2",
                    "contributions_count": 50,
                    "id": "user2",
                    "login": "user2",
                    "name": "User 2",
                }
            ],
        ]
        mock_get_top_contributors.return_value = expected

        result = await load_top_contributors_by_repository_id(repository_ids)

        assert result == expected

    @pytest.mark.asyncio
    async def test_empty_repository_ids(self):
        """An empty repository_ids list returns an empty list."""
        result = await load_top_contributors_by_repository_id([])
        assert result == []

    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.get_top_contributors_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.sync_to_async",
    )
    @pytest.mark.asyncio
    async def test_window_filter_enforces_limit(
        self, mock_sync_to_async, mock_get_top_contributors
    ):
        """The window function filter enforces TOP_CONTRIBUTORS_LIMIT."""
        repository_ids = [1]
        mock_qs = MagicMock()
        mock_annotate_result = mock_qs.filter.return_value.annotate.return_value
        self._setup_sync_to_async(mock_sync_to_async, mock_qs)
        mock_get_top_contributors.return_value = [[]]

        await load_top_contributors_by_repository_id(repository_ids)

        mock_annotate_result.filter.assert_called_once_with(row_number__lte=TOP_CONTRIBUTORS_LIMIT)


class TestGetRepositoryContributorLoaders:
    """Tests for get_repository_contributor_loaders."""

    def test_returns_mapping_with_top_contributors_loader(self):
        """Factory returns a mapping with the top contributors loader."""
        loaders = get_repository_contributor_loaders()
        assert TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER in loaders
        assert isinstance(loaders[TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_repository_contributor_loaders()
        loaders2 = get_repository_contributor_loaders()
        assert loaders1 is not loaders2
        assert (
            loaders1[TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER]
            is not loaders2[TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER]
        )

    def test_load_fn_is_load_top_contributors_by_repository_id(self):
        """The top contributors loader is wired to load_top_contributors_by_repository_id."""
        loaders = get_repository_contributor_loaders()
        loader = loaders[TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER]
        assert loader.load_fn is load_top_contributors_by_repository_id
