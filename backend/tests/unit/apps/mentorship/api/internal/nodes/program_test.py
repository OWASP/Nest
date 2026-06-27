from unittest.mock import AsyncMock, MagicMock

import pytest
import strawberry

from apps.mentorship.api.internal.dataloaders.admin import ADMINS_BY_PROGRAM_ID_LOADER
from apps.mentorship.api.internal.nodes.program import ProgramNode
from apps.mentorship.models.program import Program


class TestProgramNode:
    @pytest.mark.asyncio
    async def test_admins_uses_dataloader(self):
        """Verify admins resolver delegates to the dataloader."""
        mock_program = MagicMock(spec=Program)
        field = next(f for f in ProgramNode.__strawberry_definition__.fields if f.name == "admins")
        info = MagicMock(spec=strawberry.Info)
        mock_dataloader = AsyncMock()
        mock_dataloader.load = AsyncMock(return_value=[MagicMock(), MagicMock()])
        info.context.mentorship_dataloaders = {ADMINS_BY_PROGRAM_ID_LOADER: mock_dataloader}
        result = await field.base_resolver.wrapped_func(mock_program, mock_program, info)
        mock_dataloader.load.assert_called_once_with(mock_program.pk)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_recent_milestones(self):
        """Verify recent_milestones resolver delegates to the dataloader."""
        mock_program = MagicMock(spec=Program)
        field = next(
            f
            for f in ProgramNode.__strawberry_definition__.fields
            if f.name == "recent_milestones"
        )
        info = MagicMock(spec=strawberry.Info)
        mock_dataloader = AsyncMock()
        mock_dataloader.load = AsyncMock(return_value=[MagicMock(), MagicMock()])
        info.context.github_dataloaders = {"recent_milestones_by_program_id": mock_dataloader}
        result = await field.base_resolver.wrapped_func(mock_program, mock_program, info)
        mock_dataloader.load.assert_called_once_with(mock_program.pk)
        assert len(result) == 2
