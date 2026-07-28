"""Tests for the chapter dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.owasp.api.internal.dataloaders.chapter import (
    ENTITY_CHANNELS_BY_CHAPTER_ID_LOADER,
    ENTITY_LEADERS_BY_CHAPTER_ID_LOADER,
    Chapter,
    get_chapter_loaders,
    load_entity_channels_by_chapter_id,
    load_entity_leaders_by_chapter_id,
)


async def _async_return(value):
    return value


def _fake_sync_to_async(fn):
    return lambda *args, **kwargs: _async_return(fn(*args, **kwargs))


class TestLoadEntityChannelsByChapterId:
    """Tests for load_entity_channels_by_chapter_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.chapter.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.chapter.EntityChannel")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_filter(
        self, mock_entity_channel, mock_content_type, mock_get_results_by_keys
    ):
        """Queryset is built with the correct filter arguments."""
        chapter_ids = [1, 2, 3]
        mock_content_type_obj = MagicMock()
        mock_content_type.objects.get_for_model.return_value = mock_content_type_obj
        mock_queryset = MagicMock()
        mock_entity_channel.objects.filter.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_entity_channels_by_chapter_id(chapter_ids)

        mock_entity_channel.objects.filter.assert_called_once_with(
            entity_type=mock_content_type_obj,
            entity_id__in=chapter_ids,
            is_active=True,
            is_reviewed=True,
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.chapter.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.chapter.EntityChannel")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_entity_channel, mock_content_type, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, chapter_ids, and correct key_field."""
        chapter_ids = [10, 20]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_queryset = MagicMock()
        mock_entity_channel.objects.filter.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], []]

        await load_entity_channels_by_chapter_id(chapter_ids)

        mock_get_results_by_keys.assert_called_once_with(
            mock_queryset, chapter_ids, key_field="entity_id"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.chapter.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.chapter.EntityChannel")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_entity_channel, mock_content_type, mock_get_results_by_keys
    ):
        """The return value is exactly what get_results_by_keys resolves to."""
        mock_channel_a = MagicMock()
        mock_channel_b = MagicMock()
        expected = [[mock_channel_a, mock_channel_b], [], [mock_channel_a]]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_results_by_keys.return_value = expected

        result = await load_entity_channels_by_chapter_id([1, 2, 3])

        assert result is expected

    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.chapter.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.chapter.EntityChannel")
    @pytest.mark.asyncio
    async def test_empty_chapter_ids(
        self, mock_entity_channel, mock_content_type, mock_get_results_by_keys
    ):
        """An empty chapter_ids list results in an empty filter and empty return."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_entity_channels_by_chapter_id([])

        mock_entity_channel.objects.filter.assert_called_once_with(
            entity_type=mock_content_type.objects.get_for_model.return_value,
            entity_id__in=[],
            is_active=True,
            is_reviewed=True,
        )
        assert result == []

    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.chapter.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.chapter.EntityChannel")
    @pytest.mark.asyncio
    async def test_single_chapter_id(
        self, mock_entity_channel, mock_content_type, mock_get_results_by_keys
    ):
        """A single-element list is handled correctly end-to-end."""
        mock_channel = MagicMock()
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[mock_channel]]

        result = await load_entity_channels_by_chapter_id([42])

        mock_entity_channel.objects.filter.assert_called_once_with(
            entity_type=mock_content_type.objects.get_for_model.return_value,
            entity_id__in=[42],
            is_active=True,
            is_reviewed=True,
        )
        assert result == [[mock_channel]]

    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.chapter.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.chapter.EntityChannel")
    @pytest.mark.asyncio
    async def test_uses_chapter_content_type(
        self, mock_entity_channel, mock_content_type, mock_get_results_by_keys
    ):
        """ContentType.objects.get_for_model is called with Chapter."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[]]

        await load_entity_channels_by_chapter_id([1])

        mock_content_type.objects.get_for_model.assert_called_once_with(Chapter)


class TestLoadEntityLeadersByChapterId:
    """Tests for load_entity_leaders_by_chapter_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.chapter.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.chapter.EntityMember")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """Queryset is built with select_related, filter, and order_by in the right order."""
        chapter_ids = [1, 2, 3]
        mock_content_type_obj = MagicMock()
        mock_content_type.objects.get_for_model.return_value = mock_content_type_obj
        mock_queryset = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_entity_leaders_by_chapter_id(chapter_ids)

        mock_entity_member.objects.select_related.assert_called_once_with("member")
        mock_filter.assert_called_once_with(
            entity_type=mock_content_type_obj,
            entity_id__in=chapter_ids,
            role=mock_entity_member.Role.LEADER,
            is_active=True,
            is_reviewed=True,
        )
        mock_filter.return_value.order_by.assert_called_once_with("order")

    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.chapter.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.chapter.EntityMember")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, chapter_ids, and correct key_field."""
        chapter_ids = [10, 20]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_queryset = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], []]

        await load_entity_leaders_by_chapter_id(chapter_ids)

        mock_get_results_by_keys.assert_called_once_with(
            mock_queryset, chapter_ids, key_field="entity_id"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.chapter.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.chapter.EntityMember")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """The return value is exactly what get_results_by_keys resolves to."""
        mock_leader_a = MagicMock()
        mock_leader_b = MagicMock()
        expected = [[mock_leader_a, mock_leader_b], [], [mock_leader_a]]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = expected

        result = await load_entity_leaders_by_chapter_id([1, 2, 3])

        assert result is expected

    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.chapter.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.chapter.EntityMember")
    @pytest.mark.asyncio
    async def test_empty_chapter_ids(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """An empty chapter_ids list results in an empty filter and empty return."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_entity_leaders_by_chapter_id([])

        mock_filter.assert_called_once_with(
            entity_type=mock_content_type.objects.get_for_model.return_value,
            entity_id__in=[],
            role=mock_entity_member.Role.LEADER,
            is_active=True,
            is_reviewed=True,
        )
        assert result == []

    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.chapter.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.chapter.EntityMember")
    @pytest.mark.asyncio
    async def test_single_chapter_id(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """A single-element list is handled correctly end-to-end."""
        mock_leader = MagicMock()
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[mock_leader]]

        result = await load_entity_leaders_by_chapter_id([42])

        mock_filter.assert_called_once_with(
            entity_type=mock_content_type.objects.get_for_model.return_value,
            entity_id__in=[42],
            role=mock_entity_member.Role.LEADER,
            is_active=True,
            is_reviewed=True,
        )
        assert result == [[mock_leader]]

    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.chapter.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.chapter.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.chapter.EntityMember")
    @pytest.mark.asyncio
    async def test_uses_chapter_content_type(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """ContentType.objects.get_for_model is called with Chapter."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[]]

        await load_entity_leaders_by_chapter_id([1])

        mock_content_type.objects.get_for_model.assert_called_once_with(Chapter)


class TestGetChapterLoaders:
    """Tests for get_chapter_loaders."""

    def test_returns_mapping(self):
        """Factory always returns a Mapping with both loaders."""
        loaders = get_chapter_loaders()
        assert ENTITY_CHANNELS_BY_CHAPTER_ID_LOADER in loaders
        assert ENTITY_LEADERS_BY_CHAPTER_ID_LOADER in loaders
        assert isinstance(loaders[ENTITY_CHANNELS_BY_CHAPTER_ID_LOADER], DataLoader)
        assert isinstance(loaders[ENTITY_LEADERS_BY_CHAPTER_ID_LOADER], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_chapter_loaders()
        loaders2 = get_chapter_loaders()
        assert loaders1 is not loaders2
        assert (
            loaders1[ENTITY_CHANNELS_BY_CHAPTER_ID_LOADER]
            is not loaders2[ENTITY_CHANNELS_BY_CHAPTER_ID_LOADER]
        )
        assert (
            loaders1[ENTITY_LEADERS_BY_CHAPTER_ID_LOADER]
            is not loaders2[ENTITY_LEADERS_BY_CHAPTER_ID_LOADER]
        )

    def test_entity_channels_load_fn_is_load_entity_channels_by_chapter_id(self):
        """The channels DataLoader is wired to load_entity_channels_by_chapter_id."""
        loaders = get_chapter_loaders()
        assert (
            loaders[ENTITY_CHANNELS_BY_CHAPTER_ID_LOADER].load_fn
            is load_entity_channels_by_chapter_id
        )

    def test_entity_leaders_load_fn_is_load_entity_leaders_by_chapter_id(self):
        """The leaders DataLoader is wired to load_entity_leaders_by_chapter_id."""
        loaders = get_chapter_loaders()
        assert (
            loaders[ENTITY_LEADERS_BY_CHAPTER_ID_LOADER].load_fn
            is load_entity_leaders_by_chapter_id
        )
