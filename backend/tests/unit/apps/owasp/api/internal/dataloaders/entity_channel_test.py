"""Tests for the entity channel dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.owasp.api.internal.dataloaders.entity_channel import (
    EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER,
    NAME_BY_ENTITY_CHANNEL_ID_LOADER,
    Conversation,
    get_entity_channel_loaders,
    load_external_id_by_entity_channel_id,
    load_name_by_entity_channel_id,
)


async def _async_return(value):
    return value


def _fake_sync_to_async(fn):
    return lambda *args, **kwargs: _async_return(fn(*args, **kwargs))


class TestLoadExternalIdByEntityChannelId:
    """Tests for load_external_id_by_entity_channel_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_filter(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """Queryset is built with the correct filter arguments."""
        entity_channel_ids = [1, 2, 3]
        mock_content_type_obj = MagicMock()
        mock_content_type.objects.get_for_model.return_value = mock_content_type_obj
        mock_queryset = MagicMock()
        mock_entity_channel.objects.filter.return_value = mock_queryset
        mock_get_result_by_keys.return_value = ["slack-1", None, "slack-3"]

        await load_external_id_by_entity_channel_id(entity_channel_ids)

        mock_entity_channel.objects.filter.assert_called_once_with(
            pk__in=entity_channel_ids,
            channel_type=mock_content_type_obj,
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_delegates_to_get_result_by_keys_correct_args(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """get_result_by_keys receives the queryset, ids, and correct key/value fields."""
        entity_channel_ids = [10, 20]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filtered = MagicMock()
        mock_entity_channel.objects.filter.return_value = mock_filtered
        mock_annotated = MagicMock()
        mock_filtered.annotate.return_value = mock_annotated
        mock_get_result_by_keys.return_value = ["slack-10", None]

        await load_external_id_by_entity_channel_id(entity_channel_ids)

        mock_get_result_by_keys.assert_called_once_with(
            mock_annotated, entity_channel_ids, key_field="pk", value_field="value"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_returns_value_list_from_get_result_by_keys(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """The return value is exactly what get_result_by_keys resolves to."""
        expected = ["slack-1", None, "slack-3"]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_result_by_keys.return_value = expected

        result = await load_external_id_by_entity_channel_id([1, 2, 3])

        assert result == expected

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_empty_entity_channel_ids(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """An empty entity_channel_ids list results in an empty filter and empty return."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_result_by_keys.return_value = []

        result = await load_external_id_by_entity_channel_id([])

        mock_entity_channel.objects.filter.assert_called_once_with(
            pk__in=[],
            channel_type=mock_content_type.objects.get_for_model.return_value,
        )
        assert result == []

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_single_entity_channel_id(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """A single-element list is handled correctly end-to-end."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_result_by_keys.return_value = ["slack-42"]

        result = await load_external_id_by_entity_channel_id([42])

        mock_entity_channel.objects.filter.assert_called_once_with(
            pk__in=[42],
            channel_type=mock_content_type.objects.get_for_model.return_value,
        )
        assert result == ["slack-42"]

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_uses_conversation_content_type(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """ContentType.objects.get_for_model is called with Conversation."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_result_by_keys.return_value = [None]

        await load_external_id_by_entity_channel_id([1])

        mock_content_type.objects.get_for_model.assert_called_once_with(Conversation)

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_preserves_empty_string(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """Empty strings returned by get_result_by_keys are preserved."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_result_by_keys.return_value = ["", "slack-2"]

        result = await load_external_id_by_entity_channel_id([1, 2])

        assert result == ["", "slack-2"]


class TestLoadNameByEntityChannelId:
    """Tests for load_name_by_entity_channel_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_filter(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """Queryset is built with the correct filter arguments."""
        entity_channel_ids = [1, 2, 3]
        mock_content_type_obj = MagicMock()
        mock_content_type.objects.get_for_model.return_value = mock_content_type_obj
        mock_queryset = MagicMock()
        mock_entity_channel.objects.filter.return_value = mock_queryset
        mock_get_result_by_keys.return_value = ["name-1", None, "name-3"]

        await load_name_by_entity_channel_id(entity_channel_ids)

        mock_entity_channel.objects.filter.assert_called_once_with(
            pk__in=entity_channel_ids,
            channel_type=mock_content_type_obj,
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_delegates_to_get_result_by_keys_correct_args(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """get_result_by_keys receives the queryset, ids, and correct key/value fields."""
        entity_channel_ids = [10, 20]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filtered = MagicMock()
        mock_entity_channel.objects.filter.return_value = mock_filtered
        mock_annotated = MagicMock()
        mock_filtered.annotate.return_value = mock_annotated
        mock_get_result_by_keys.return_value = ["name-10", None]

        await load_name_by_entity_channel_id(entity_channel_ids)

        mock_get_result_by_keys.assert_called_once_with(
            mock_annotated, entity_channel_ids, key_field="pk", value_field="value"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_returns_value_list_from_get_result_by_keys(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """The return value is exactly what get_result_by_keys resolves to."""
        expected = ["name-1", None, "name-3"]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_result_by_keys.return_value = expected

        result = await load_name_by_entity_channel_id([1, 2, 3])

        assert result == expected

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_empty_entity_channel_ids(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """An empty entity_channel_ids list results in an empty filter and empty return."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_result_by_keys.return_value = []

        result = await load_name_by_entity_channel_id([])

        mock_entity_channel.objects.filter.assert_called_once_with(
            pk__in=[],
            channel_type=mock_content_type.objects.get_for_model.return_value,
        )
        assert result == []

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_single_entity_channel_id(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """A single-element list is handled correctly end-to-end."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_result_by_keys.return_value = ["name-42"]

        result = await load_name_by_entity_channel_id([42])

        mock_entity_channel.objects.filter.assert_called_once_with(
            pk__in=[42],
            channel_type=mock_content_type.objects.get_for_model.return_value,
        )
        assert result == ["name-42"]

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_uses_conversation_content_type(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """ContentType.objects.get_for_model is called with Conversation."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_result_by_keys.return_value = [None]

        await load_name_by_entity_channel_id([1])

        mock_content_type.objects.get_for_model.assert_called_once_with(Conversation)

    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.entity_channel.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.entity_channel.EntityChannel")
    @pytest.mark.asyncio
    async def test_preserves_empty_string(
        self, mock_entity_channel, mock_content_type, mock_get_result_by_keys
    ):
        """Empty strings returned by get_result_by_keys are preserved."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_result_by_keys.return_value = ["", "name-2"]

        result = await load_name_by_entity_channel_id([1, 2])

        assert result == ["", "name-2"]


class TestGetEntityChannelLoaders:
    """Tests for get_entity_channel_loaders."""

    def test_returns_mapping(self):
        """Factory returns a Mapping with both loaders."""
        loaders = get_entity_channel_loaders()
        assert EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER in loaders
        assert NAME_BY_ENTITY_CHANNEL_ID_LOADER in loaders
        assert isinstance(loaders[EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER], DataLoader)
        assert isinstance(loaders[NAME_BY_ENTITY_CHANNEL_ID_LOADER], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_entity_channel_loaders()
        loaders2 = get_entity_channel_loaders()
        assert loaders1 is not loaders2
        assert (
            loaders1[EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER]
            is not loaders2[EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER]
        )
        assert (
            loaders1[NAME_BY_ENTITY_CHANNEL_ID_LOADER]
            is not loaders2[NAME_BY_ENTITY_CHANNEL_ID_LOADER]
        )

    def test_external_id_load_fn(self):
        """The external_id DataLoader is wired to load_external_id_by_entity_channel_id."""
        loaders = get_entity_channel_loaders()
        assert (
            loaders[EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER].load_fn
            is load_external_id_by_entity_channel_id
        )

    def test_name_load_fn(self):
        """The name DataLoader is wired to load_name_by_entity_channel_id."""
        loaders = get_entity_channel_loaders()
        assert loaders[NAME_BY_ENTITY_CHANNEL_ID_LOADER].load_fn is load_name_by_entity_channel_id
