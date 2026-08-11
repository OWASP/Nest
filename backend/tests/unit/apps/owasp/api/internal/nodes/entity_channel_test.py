"""Tests for EntityChannel GraphQL node resolvers."""

from unittest.mock import AsyncMock, Mock

import pytest

from apps.owasp.api.internal.dataloaders.entity_channel import (
    EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER,
    NAME_BY_ENTITY_CHANNEL_ID_LOADER,
)
from apps.owasp.api.internal.nodes.entity_channel import EntityChannelNode


class TestEntityChannelNodeResolvers:
    def _get_resolver(self, field_name):
        """Get the resolver function for a field."""
        for field in EntityChannelNode.__strawberry_definition__.fields:
            if field.name == field_name:
                return field.base_resolver.wrapped_func if field.base_resolver else None
        return None

    @pytest.mark.asyncio
    async def test_external_id_resolver_uses_dataloader(self):
        """external_id resolver delegates to the dataloader with pk."""
        mock_entity_channel = Mock()
        mock_entity_channel.pk = 42

        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value="C123ABC")
        mock_info = Mock()
        mock_info.context.owasp_dataloaders = {
            EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER: mock_loader,
        }

        resolver = self._get_resolver("external_id")
        result = await resolver(None, mock_entity_channel, mock_info)

        assert result == "C123ABC"
        mock_loader.load.assert_awaited_once_with(42)

    @pytest.mark.asyncio
    async def test_name_resolver_uses_dataloader(self):
        """Name resolver delegates to the dataloader with pk."""
        mock_entity_channel = Mock()
        mock_entity_channel.pk = 99

        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value="chapter-general")
        mock_info = Mock()
        mock_info.context.owasp_dataloaders = {
            NAME_BY_ENTITY_CHANNEL_ID_LOADER: mock_loader,
        }

        resolver = self._get_resolver("name")
        result = await resolver(None, mock_entity_channel, mock_info)

        assert result == "chapter-general"
        mock_loader.load.assert_awaited_once_with(99)

    @pytest.mark.asyncio
    async def test_external_id_resolver_returns_none(self):
        """external_id resolver returns None when dataloader returns None."""
        mock_entity_channel = Mock()
        mock_entity_channel.pk = 1

        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=None)
        mock_info = Mock()
        mock_info.context.owasp_dataloaders = {
            EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER: mock_loader,
        }

        resolver = self._get_resolver("external_id")
        result = await resolver(None, mock_entity_channel, mock_info)

        assert result is None

    @pytest.mark.asyncio
    async def test_name_resolver_returns_none(self):
        """Name resolver returns None when dataloader returns None."""
        mock_entity_channel = Mock()
        mock_entity_channel.pk = 1

        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=None)
        mock_info = Mock()
        mock_info.context.owasp_dataloaders = {
            NAME_BY_ENTITY_CHANNEL_ID_LOADER: mock_loader,
        }

        resolver = self._get_resolver("name")
        result = await resolver(None, mock_entity_channel, mock_info)

        assert result is None
