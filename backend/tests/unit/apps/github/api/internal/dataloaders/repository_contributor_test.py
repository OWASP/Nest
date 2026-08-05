"""Tests for repository contributor dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from django.db.models import F, Sum, Window
from django.db.models.functions import RowNumber
from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.repository_contributor import (
    TOP_CONTRIBUTORS_BY_CHAPTER_ID_LOADER,
    TOP_CONTRIBUTORS_BY_PROJECT_ID_LOADER,
    TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER,
    TOP_CONTRIBUTORS_LIMIT,
    get_repository_contributor_loaders,
    load_top_contributors_by_chapter_id,
    load_top_contributors_by_project_id,
    load_top_contributors_by_repository_id,
)


class TestLoadTopContributorsByRepositoryId:
    """Tests for load_top_contributors_by_repository_id."""

    @staticmethod
    def _setup_sync_to_async(mock_sync_to_async, mock_qs):
        """Configure sync_to_async mock: returns a callable that returns an awaitable."""
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_qs)

    @staticmethod
    def _ordered_qs(mock_qs):
        """Return the mock queryset at the end of the repository contributors chain."""
        filtered = mock_qs.filter.return_value
        annotated = filtered.annotate.return_value
        ranked = annotated.filter.return_value
        values = ranked.values.return_value
        return values.order_by.return_value

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
        """Queryset is built with filter, annotate (window), filter, values, order_by."""
        repository_ids = [1, 2, 3]
        mock_qs = MagicMock()
        self._setup_sync_to_async(mock_sync_to_async, mock_qs)
        mock_get_top_contributors.return_value = [[], [], []]

        await load_top_contributors_by_repository_id(repository_ids)

        mock_qs.filter.assert_called_once_with(repository_id__in=repository_ids)
        mock_qs.filter.return_value.annotate.assert_called_once()
        mock_qs.filter.return_value.annotate.return_value.filter.assert_called_once()
        mock_qs.filter.return_value.annotate.return_value.filter.return_value.values.assert_called_once()
        mock_qs.filter.return_value.annotate.return_value.filter.return_value.values.return_value.order_by.assert_called_once_with(
            "repository_id", "-contributions_count"
        )

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
        self._setup_sync_to_async(mock_sync_to_async, mock_qs)
        mock_get_top_contributors.return_value = [[], []]

        await load_top_contributors_by_repository_id(repository_ids)

        mock_get_top_contributors.assert_called_once_with(
            queryset=self._ordered_qs(mock_qs), keys=repository_ids, key_field="repository_id"
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
        self._setup_sync_to_async(mock_sync_to_async, mock_qs)
        mock_get_top_contributors.return_value = [[]]

        await load_top_contributors_by_repository_id(repository_ids)

        mock_qs.filter.return_value.annotate.return_value.filter.assert_called_once_with(
            row_number__lte=TOP_CONTRIBUTORS_LIMIT
        )


class TestLoadTopContributorsByProjectId:
    """Tests for load_top_contributors_by_project_id."""

    @staticmethod
    def _setup_sync_to_async(mock_sync_to_async, mock_qs):
        """Configure sync_to_async mock: returns a callable that returns an awaitable."""
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_qs)

    @staticmethod
    def _ordered_qs(mock_qs):
        """Return the mock queryset at the end of the project contributors chain."""
        filtered = mock_qs.filter.return_value
        values = filtered.values.return_value
        summed = values.annotate.return_value
        ranked = summed.annotate.return_value
        windowed = ranked.filter.return_value
        return windowed.order_by.return_value

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
        """Queryset is built with filter, values, annotate Sum/Window, filter, order_by."""
        project_ids = [1, 2, 3]
        mock_qs = MagicMock()
        self._setup_sync_to_async(mock_sync_to_async, mock_qs)
        mock_get_top_contributors.return_value = [[], [], []]

        await load_top_contributors_by_project_id(project_ids)

        mock_qs.filter.assert_called_once_with(repository__project__in=project_ids)
        mock_qs.filter.return_value.values.assert_called_once_with(
            avatar_url=F("user__avatar_url"),
            login=F("user__login"),
            name=F("user__name"),
            project_id=F("repository__project__id"),
        )
        mock_qs.filter.return_value.values.return_value.annotate.assert_called_once_with(
            contributions_count=Sum("contributions_count")
        )
        mock_qs.filter.return_value.values.return_value.annotate.return_value.annotate.assert_called_once_with(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("project_id")],
                order_by=F("contributions_count").desc(),
            )
        )
        mock_qs.filter.return_value.values.return_value.annotate.return_value.annotate.return_value.filter.assert_called_once_with(
            row_number__lte=TOP_CONTRIBUTORS_LIMIT
        )
        mock_qs.filter.return_value.values.return_value.annotate.return_value.annotate.return_value.filter.return_value.order_by.assert_called_once_with(
            "project_id", "-contributions_count"
        )

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
        project_ids = [10, 20]
        mock_qs = MagicMock()
        self._setup_sync_to_async(mock_sync_to_async, mock_qs)
        mock_get_top_contributors.return_value = [[], []]

        await load_top_contributors_by_project_id(project_ids)

        mock_get_top_contributors.assert_called_once_with(
            queryset=self._ordered_qs(mock_qs),
            keys=project_ids,
            key_field="project_id",
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
        project_ids = [1, 2]
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

        result = await load_top_contributors_by_project_id(project_ids)

        assert result == expected

    @pytest.mark.asyncio
    async def test_empty_project_ids(self):
        """An empty project_ids list returns an empty list."""
        result = await load_top_contributors_by_project_id([])
        assert result == []


class TestLoadTopContributorsByChapterId:
    """Tests for load_top_contributors_by_chapter_id."""

    @staticmethod
    def _setup_sync_to_async(mock_sync_to_async, mock_qs):
        """Configure sync_to_async mock: returns a callable that returns an awaitable."""
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_qs)

    @staticmethod
    def _setup_chapter_objects(mock_chapter_objects):
        """Configure Chapter.objects mock to return subquery objects."""
        mock_chapter_repository_ids = MagicMock()
        mock_chapter_id_subquery = MagicMock()
        mock_chapter_objects.filter.return_value.values.side_effect = [
            mock_chapter_repository_ids,
            mock_chapter_id_subquery,
        ]
        return mock_chapter_repository_ids, mock_chapter_id_subquery

    @staticmethod
    def _ordered_qs(mock_qs):
        """Return the mock queryset at the end of the chapter contributors chain."""
        filtered = mock_qs.filter.return_value
        annotated = filtered.annotate.return_value
        ranked = annotated.filter.return_value
        values = ranked.values.return_value
        return values.order_by.return_value

    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.Chapter.objects",
    )
    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.get_top_contributors_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.sync_to_async",
    )
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self,
        mock_sync_to_async,
        mock_get_top_contributors,
        mock_chapter_objects,
    ):
        """Queryset is built with filter, annotate, filter, values, order_by."""
        chapter_ids = [1, 2, 3]
        mock_qs = MagicMock()
        self._setup_sync_to_async(mock_sync_to_async, mock_qs)
        mock_chapter_repository_ids, _ = self._setup_chapter_objects(mock_chapter_objects)
        mock_get_top_contributors.return_value = [[], [], []]

        await load_top_contributors_by_chapter_id(chapter_ids)

        mock_qs.filter.assert_called_once_with(repository_id__in=mock_chapter_repository_ids)
        mock_qs.filter.return_value.annotate.assert_called_once()
        mock_qs.filter.return_value.annotate.return_value.filter.assert_called_once()
        mock_qs.filter.return_value.annotate.return_value.filter.return_value.values.assert_called_once()
        mock_qs.filter.return_value.annotate.return_value.filter.return_value.values.return_value.order_by.assert_called_once_with(
            "chapter_id", "-contributions_count"
        )

    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.Chapter.objects",
    )
    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.get_top_contributors_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.sync_to_async",
    )
    @pytest.mark.asyncio
    async def test_delegates_to_get_top_contributors_by_keys(
        self,
        mock_sync_to_async,
        mock_get_top_contributors,
        mock_chapter_objects,
    ):
        """Delegates to get_top_contributors_by_keys keyed by chapter_id."""
        chapter_ids = [10, 20]
        mock_qs = MagicMock()
        self._setup_sync_to_async(mock_sync_to_async, mock_qs)
        self._setup_chapter_objects(mock_chapter_objects)
        mock_get_top_contributors.return_value = [[], []]

        await load_top_contributors_by_chapter_id(chapter_ids)

        mock_get_top_contributors.assert_called_once_with(
            queryset=self._ordered_qs(mock_qs),
            keys=chapter_ids,
            key_field="chapter_id",
        )

    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.Chapter.objects",
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
        self,
        mock_sync_to_async,
        mock_get_top_contributors,
        mock_chapter_objects,
    ):
        """Return value is exactly what get_top_contributors_by_keys resolves to."""
        chapter_ids = [1, 2]
        mock_qs = MagicMock()
        self._setup_sync_to_async(mock_sync_to_async, mock_qs)
        self._setup_chapter_objects(mock_chapter_objects)
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

        result = await load_top_contributors_by_chapter_id(chapter_ids)

        assert result == expected

    @pytest.mark.asyncio
    async def test_empty_chapter_ids(self):
        """An empty chapter_ids list returns an empty list."""
        result = await load_top_contributors_by_chapter_id([])
        assert result == []

    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.Chapter.objects",
    )
    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.get_top_contributors_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.github.api.internal.dataloaders.repository_contributor.sync_to_async",
    )
    @pytest.mark.asyncio
    async def test_window_filter_enforces_limit(
        self,
        mock_sync_to_async,
        mock_get_top_contributors,
        mock_chapter_objects,
    ):
        """The window function filter enforces TOP_CONTRIBUTORS_LIMIT."""
        chapter_ids = [1]
        mock_qs = MagicMock()
        self._setup_sync_to_async(mock_sync_to_async, mock_qs)
        self._setup_chapter_objects(mock_chapter_objects)
        mock_get_top_contributors.return_value = [[]]

        await load_top_contributors_by_chapter_id(chapter_ids)

        mock_qs.filter.return_value.annotate.return_value.filter.assert_called_once_with(
            row_number__lte=TOP_CONTRIBUTORS_LIMIT
        )


class TestGetRepositoryContributorLoaders:
    """Tests for get_repository_contributor_loaders."""

    @pytest.mark.parametrize(
        "loader_key",
        [
            TOP_CONTRIBUTORS_BY_CHAPTER_ID_LOADER,
            TOP_CONTRIBUTORS_BY_PROJECT_ID_LOADER,
            TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER,
        ],
    )
    def test_returns_mapping(self, loader_key):
        """Factory returns a mapping with each contributor loader."""
        loaders = get_repository_contributor_loaders()
        assert loader_key in loaders
        assert isinstance(loaders[loader_key], DataLoader)

    def test_load_fn_is_load_top_contributors_by_chapter_id(self):
        """The chapter loader is wired to load_top_contributors_by_chapter_id."""
        loaders = get_repository_contributor_loaders()
        loader = loaders[TOP_CONTRIBUTORS_BY_CHAPTER_ID_LOADER]
        assert loader.load_fn is load_top_contributors_by_chapter_id

    def test_load_fn_is_load_top_contributors_by_project_id(self):
        """The project loader is wired to load_top_contributors_by_project_id."""
        loaders = get_repository_contributor_loaders()
        loader = loaders[TOP_CONTRIBUTORS_BY_PROJECT_ID_LOADER]
        assert loader.load_fn is load_top_contributors_by_project_id

    def test_load_fn_is_load_top_contributors_by_repository_id(self):
        """The repository loader is wired to load_top_contributors_by_repository_id."""
        loaders = get_repository_contributor_loaders()
        loader = loaders[TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER]
        assert loader.load_fn is load_top_contributors_by_repository_id

    @pytest.mark.parametrize(
        "loader_key",
        [
            TOP_CONTRIBUTORS_BY_CHAPTER_ID_LOADER,
            TOP_CONTRIBUTORS_BY_PROJECT_ID_LOADER,
            TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER,
        ],
    )
    def test_returns_new_instances_on_each_call(self, loader_key):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_repository_contributor_loaders()
        loaders2 = get_repository_contributor_loaders()
        assert loaders1 is not loaders2
        assert loaders1[loader_key] is not loaders2[loader_key]
