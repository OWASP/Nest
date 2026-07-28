"""Tests for committee dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.owasp.api.internal.dataloaders.committee import (
    ENTITY_CHANNELS_BY_COMMITTEE_ID,
    ENTITY_LEADERS_BY_COMMITTEE_ID,
    Committee,
    get_committee_loaders,
    load_entity_channels_by_committee_id,
    load_entity_leaders_by_committee_id,
)


async def _async_return(value):
    return value


def _fake_sync_to_async(fn):
    return lambda *args, **kwargs: _async_return(fn(*args, **kwargs))


class TestLoadEntityChannelsByCommitteeId:
    """Tests for load_entity_channels_by_committee_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.committee.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.committee.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.committee.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.committee.EntityChannel")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_filter(
        self, mock_entity_channel, mock_content_type, mock_get_results_by_keys
    ):
        """Queryset is built with the correct filter arguments."""
        committee_ids = [1, 2, 3]
        mock_content_type_obj = MagicMock()
        mock_content_type.objects.get_for_model.return_value = mock_content_type_obj
        mock_queryset = MagicMock()
        mock_entity_channel.objects.filter.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_entity_channels_by_committee_id(committee_ids)

        mock_entity_channel.objects.filter.assert_called_once_with(
            entity_type=mock_content_type_obj,
            entity_id__in=committee_ids,
            is_active=True,
            is_reviewed=True,
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.committee.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.committee.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.committee.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.committee.EntityChannel")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_entity_channel, mock_content_type, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, committee_ids, and correct key_field."""
        committee_ids = [10, 20]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_queryset = MagicMock()
        mock_entity_channel.objects.filter.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], []]

        await load_entity_channels_by_committee_id(committee_ids)

        mock_get_results_by_keys.assert_called_once_with(
            mock_queryset, committee_ids, key_field="entity_id"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.committee.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.committee.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.committee.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.committee.EntityChannel")
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

        result = await load_entity_channels_by_committee_id([1, 2, 3])

        assert result is expected

    @patch(
        "apps.owasp.api.internal.dataloaders.committee.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.committee.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.committee.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.committee.EntityChannel")
    @pytest.mark.asyncio
    async def test_empty_committee_ids(
        self, mock_entity_channel, mock_content_type, mock_get_results_by_keys
    ):
        """An empty committee_ids list results in an empty filter and empty return."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_entity_channels_by_committee_id([])

        mock_entity_channel.objects.filter.assert_called_once_with(
            entity_type=mock_content_type.objects.get_for_model.return_value,
            entity_id__in=[],
            is_active=True,
            is_reviewed=True,
        )
        assert result == []

    @patch(
        "apps.owasp.api.internal.dataloaders.committee.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.committee.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.committee.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.committee.EntityChannel")
    @pytest.mark.asyncio
    async def test_single_committee_id(
        self, mock_entity_channel, mock_content_type, mock_get_results_by_keys
    ):
        """A single-element list is handled correctly end-to-end."""
        mock_channel = MagicMock()
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[mock_channel]]

        result = await load_entity_channels_by_committee_id([42])

        mock_entity_channel.objects.filter.assert_called_once_with(
            entity_type=mock_content_type.objects.get_for_model.return_value,
            entity_id__in=[42],
            is_active=True,
            is_reviewed=True,
        )
        assert result == [[mock_channel]]

    @patch(
        "apps.owasp.api.internal.dataloaders.committee.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.committee.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.committee.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.committee.EntityChannel")
    @pytest.mark.asyncio
    async def test_uses_committee_content_type(
        self, mock_entity_channel, mock_content_type, mock_get_results_by_keys
    ):
        """ContentType.objects.get_for_model is called with Committee."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_entity_channel.objects.filter.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[]]

        await load_entity_channels_by_committee_id([1])

        mock_content_type.objects.get_for_model.assert_called_once_with(Committee)


class TestLoadEntityLeadersByCommitteeId:
    """Tests for load_entity_leaders_by_committee_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.committee.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.committee.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.committee.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.committee.EntityMember")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """Queryset is built with select_related, filter, and order_by in the right order."""
        committee_ids = [1, 2, 3]
        mock_content_type_obj = MagicMock()
        mock_content_type.objects.get_for_model.return_value = mock_content_type_obj
        mock_queryset = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_entity_leaders_by_committee_id(committee_ids)

        mock_entity_member.objects.select_related.assert_called_once_with("member")
        mock_filter.assert_called_once_with(
            entity_type=mock_content_type_obj,
            entity_id__in=committee_ids,
            role=mock_entity_member.Role.LEADER,
            is_active=True,
            is_reviewed=True,
        )
        mock_filter.return_value.order_by.assert_called_once_with("order")

    @patch(
        "apps.owasp.api.internal.dataloaders.committee.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.committee.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.committee.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.committee.EntityMember")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, committee_ids, and correct key_field."""
        committee_ids = [10, 20]
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_queryset = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = mock_queryset
        mock_get_results_by_keys.return_value = [[], []]

        await load_entity_leaders_by_committee_id(committee_ids)

        mock_get_results_by_keys.assert_called_once_with(
            mock_queryset, committee_ids, key_field="entity_id"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.committee.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.committee.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.committee.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.committee.EntityMember")
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

        result = await load_entity_leaders_by_committee_id([1, 2, 3])

        assert result is expected

    @patch(
        "apps.owasp.api.internal.dataloaders.committee.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.committee.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.committee.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.committee.EntityMember")
    @pytest.mark.asyncio
    async def test_empty_committee_ids(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """An empty committee_ids list results in an empty filter and empty return."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_entity_leaders_by_committee_id([])

        mock_filter.assert_called_once_with(
            entity_type=mock_content_type.objects.get_for_model.return_value,
            entity_id__in=[],
            role=mock_entity_member.Role.LEADER,
            is_active=True,
            is_reviewed=True,
        )
        assert result == []

    @patch(
        "apps.owasp.api.internal.dataloaders.committee.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.committee.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.committee.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.committee.EntityMember")
    @pytest.mark.asyncio
    async def test_single_committee_id(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """A single-element list is handled correctly end-to-end."""
        mock_leader = MagicMock()
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[mock_leader]]

        result = await load_entity_leaders_by_committee_id([42])

        mock_filter.assert_called_once_with(
            entity_type=mock_content_type.objects.get_for_model.return_value,
            entity_id__in=[42],
            role=mock_entity_member.Role.LEADER,
            is_active=True,
            is_reviewed=True,
        )
        assert result == [[mock_leader]]

    @patch(
        "apps.owasp.api.internal.dataloaders.committee.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch(
        "apps.owasp.api.internal.dataloaders.committee.sync_to_async",
        new=_fake_sync_to_async,
    )
    @patch("apps.owasp.api.internal.dataloaders.committee.ContentType")
    @patch("apps.owasp.api.internal.dataloaders.committee.EntityMember")
    @pytest.mark.asyncio
    async def test_uses_committee_content_type(
        self, mock_entity_member, mock_content_type, mock_get_results_by_keys
    ):
        """ContentType.objects.get_for_model is called with Committee."""
        mock_content_type.objects.get_for_model.return_value = MagicMock()
        mock_filter = mock_entity_member.objects.select_related.return_value.filter
        mock_filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[]]

        await load_entity_leaders_by_committee_id([1])

        mock_content_type.objects.get_for_model.assert_called_once_with(Committee)


class TestGetCommitteeLoaders:
    """Tests for get_committee_loaders."""

    @pytest.mark.parametrize(
        "loader_key",
        [
            ENTITY_CHANNELS_BY_COMMITTEE_ID,
            ENTITY_LEADERS_BY_COMMITTEE_ID,
        ],
    )
    def test_returns_mapping(self, loader_key):
        """Factory always returns a Mapping."""
        loaders = get_committee_loaders()
        assert loader_key in loaders
        assert isinstance(loaders[loader_key], DataLoader)

    def test_load_fn_is_load_entity_channels_by_committee_id(self):
        """The channels loader is wired to load_entity_channels_by_committee_id."""
        loaders = get_committee_loaders()
        assert (
            loaders[ENTITY_CHANNELS_BY_COMMITTEE_ID].load_fn
            is load_entity_channels_by_committee_id
        )

    def test_load_fn_is_load_entity_leaders_by_committee_id(self):
        """The leaders loader is wired to load_entity_leaders_by_committee_id."""
        loaders = get_committee_loaders()
        assert (
            loaders[ENTITY_LEADERS_BY_COMMITTEE_ID].load_fn is load_entity_leaders_by_committee_id
        )

    @pytest.mark.parametrize(
        "loader_key",
        [
            ENTITY_CHANNELS_BY_COMMITTEE_ID,
            ENTITY_LEADERS_BY_COMMITTEE_ID,
        ],
    )
    def test_returns_new_instances_on_each_call(self, loader_key):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_committee_loaders()
        loaders2 = get_committee_loaders()
        assert loaders1 is not loaders2
        assert loaders1[loader_key] is not loaders2[loader_key]
