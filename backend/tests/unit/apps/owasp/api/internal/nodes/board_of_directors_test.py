"""Tests for BoardOfDirectors GraphQL node."""

from unittest.mock import AsyncMock, MagicMock

import pytest
import strawberry

from apps.owasp.api.internal.dataloaders.board_of_directors import (
    CANDIDATES_BY_BOARD_ID_LOADER,
    MEMBERS_BY_BOARD_ID_LOADER,
)
from apps.owasp.api.internal.nodes.board_of_directors import BoardOfDirectorsNode
from apps.owasp.models.board_of_directors import BoardOfDirectors
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestBoardOfDirectorsNode(GraphQLNodeBaseTest):
    """Test cases for BoardOfDirectorsNode class."""

    def test_node_fields(self):
        field_names = {
            field.name for field in BoardOfDirectorsNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "_id",
            "candidates",
            "created_at",
            "members",
            "owasp_url",
            "updated_at",
            "year",
        }
        assert field_names == expected_field_names

    def test_owasp_url_resolver(self):
        """Test owasp_url returns URL from board instance."""
        mock_board = MagicMock(spec=BoardOfDirectors)
        mock_board.owasp_url = "https://board.owasp.org/elections/2025_elections"

        field = self._get_field_by_name("owasp_url", BoardOfDirectorsNode)
        result = field.base_resolver.wrapped_func(None, mock_board)

        assert result == "https://board.owasp.org/elections/2025_elections"

    @pytest.mark.asyncio
    async def test_candidates_resolver_uses_dataloader(self):
        """Test candidates resolver delegates to the candidates dataloader."""
        mock_board = MagicMock(spec=BoardOfDirectors)
        mock_candidate1 = MagicMock()
        mock_candidate2 = MagicMock()

        field = self._get_field_by_name("candidates", BoardOfDirectorsNode)
        info = MagicMock(spec=strawberry.Info)
        mock_dataloader = AsyncMock()
        mock_dataloader.load = AsyncMock(return_value=[mock_candidate1, mock_candidate2])
        info.context.owasp_dataloaders = {CANDIDATES_BY_BOARD_ID_LOADER: mock_dataloader}

        result = await field.base_resolver.wrapped_func(mock_board, mock_board, info)

        mock_dataloader.load.assert_called_once_with(mock_board.pk)
        assert result == [mock_candidate1, mock_candidate2]

    @pytest.mark.asyncio
    async def test_members_resolver_uses_dataloader(self):
        """Test members resolver delegates to the members dataloader."""
        mock_board = MagicMock(spec=BoardOfDirectors)
        mock_member1 = MagicMock()
        mock_member2 = MagicMock()

        field = self._get_field_by_name("members", BoardOfDirectorsNode)
        info = MagicMock(spec=strawberry.Info)
        mock_dataloader = AsyncMock()
        mock_dataloader.load = AsyncMock(return_value=[mock_member1, mock_member2])
        info.context.owasp_dataloaders = {MEMBERS_BY_BOARD_ID_LOADER: mock_dataloader}

        result = await field.base_resolver.wrapped_func(mock_board, mock_board, info)

        mock_dataloader.load.assert_called_once_with(mock_board.pk)
        assert result == [mock_member1, mock_member2]
