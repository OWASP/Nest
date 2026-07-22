"""Test cases for SnapshotNode."""

from unittest.mock import AsyncMock, MagicMock

import pytest
import strawberry

from apps.owasp.api.internal.dataloaders.snapshot import (
    NEW_CHAPTERS_BY_SNAPSHOT_ID,
    NEW_ISSUES_BY_SNAPSHOT_ID,
    NEW_PROJECTS_BY_SNAPSHOT_ID,
    NEW_RELEASES_BY_SNAPSHOT_ID,
    NEW_USERS_BY_SNAPSHOT_ID,
)
from apps.owasp.api.internal.nodes.snapshot import SnapshotNode
from apps.owasp.models.snapshot import Snapshot
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestSnapshotNode(GraphQLNodeBaseTest):
    """Test cases for SnapshotNode."""

    def test_snapshot_node_inheritance(self):
        """Test SnapshotNode has strawberry definition."""
        assert hasattr(SnapshotNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        """Test expected fields are present."""
        field_names = {field.name for field in SnapshotNode.__strawberry_definition__.fields}
        expected_field_names = {
            "created_at",
            "end_at",
            "key",
            "new_chapters",
            "new_issues",
            "new_projects",
            "new_releases",
            "new_users",
            "start_at",
            "title",
        }
        assert expected_field_names.issubset(field_names)


class TestSnapshotNodeResolvers:
    """Test SnapshotNode resolver execution."""

    def _get_resolver(self, field_name):
        """Get the resolver function for a field."""
        for field in SnapshotNode.__strawberry_definition__.fields:
            if field.name == field_name:
                return field.base_resolver.wrapped_func if field.base_resolver else None
        return None

    def test_key_resolver(self):
        """Test key resolver returns snapshot key."""
        resolver = self._get_resolver("key")
        mock_snapshot = MagicMock()
        mock_snapshot.key = "2025-02"

        result = resolver(None, mock_snapshot)

        assert result == "2025-02"

    @pytest.mark.asyncio
    async def test_new_chapters_resolver_uses_dataloader(self):
        """Test new_chapters resolver delegates to the new_chapters dataloader."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_chapter1 = MagicMock()
        mock_chapter2 = MagicMock()

        resolver = self._get_resolver("new_chapters")
        info = MagicMock(spec=strawberry.Info)
        mock_dataloader = AsyncMock()
        mock_dataloader.load = AsyncMock(return_value=[mock_chapter1, mock_chapter2])
        info.context.owasp_dataloaders = {NEW_CHAPTERS_BY_SNAPSHOT_ID: mock_dataloader}

        result = await resolver(None, mock_snapshot, info)

        mock_dataloader.load.assert_called_once_with(mock_snapshot.pk)
        assert result == [mock_chapter1, mock_chapter2]

    @pytest.mark.asyncio
    async def test_new_issues_resolver_uses_dataloader(self):
        """Test new_issues resolver delegates to the new_issues dataloader."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_issue1 = MagicMock()
        mock_issue2 = MagicMock()

        resolver = self._get_resolver("new_issues")
        info = MagicMock(spec=strawberry.Info)
        mock_dataloader = AsyncMock()
        mock_dataloader.load = AsyncMock(return_value=[mock_issue1, mock_issue2])
        info.context.owasp_dataloaders = {NEW_ISSUES_BY_SNAPSHOT_ID: mock_dataloader}

        result = await resolver(None, mock_snapshot, info)

        mock_dataloader.load.assert_called_once_with(mock_snapshot.pk)
        assert result == [mock_issue1, mock_issue2]

    @pytest.mark.asyncio
    async def test_new_projects_resolver_uses_dataloader(self):
        """Test new_projects resolver delegates to the new_projects dataloader."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_project1 = MagicMock()
        mock_project2 = MagicMock()

        resolver = self._get_resolver("new_projects")
        info = MagicMock(spec=strawberry.Info)
        mock_dataloader = AsyncMock()
        mock_dataloader.load = AsyncMock(return_value=[mock_project1, mock_project2])
        info.context.owasp_dataloaders = {NEW_PROJECTS_BY_SNAPSHOT_ID: mock_dataloader}

        result = await resolver(None, mock_snapshot, info)

        mock_dataloader.load.assert_called_once_with(mock_snapshot.pk)
        assert result == [mock_project1, mock_project2]

    @pytest.mark.asyncio
    async def test_new_releases_resolver_uses_dataloader(self):
        """Test new_releases resolver delegates to the new_releases dataloader."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_release1 = MagicMock()
        mock_release2 = MagicMock()

        resolver = self._get_resolver("new_releases")
        info = MagicMock(spec=strawberry.Info)
        mock_dataloader = AsyncMock()
        mock_dataloader.load = AsyncMock(return_value=[mock_release1, mock_release2])
        info.context.owasp_dataloaders = {NEW_RELEASES_BY_SNAPSHOT_ID: mock_dataloader}

        result = await resolver(None, mock_snapshot, info)

        mock_dataloader.load.assert_called_once_with(mock_snapshot.pk)
        assert result == [mock_release1, mock_release2]

    @pytest.mark.asyncio
    async def test_new_users_resolver_uses_dataloader(self):
        """Test new_users resolver delegates to the new_users dataloader."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_user1 = MagicMock()
        mock_user2 = MagicMock()

        resolver = self._get_resolver("new_users")
        info = MagicMock(spec=strawberry.Info)
        mock_dataloader = AsyncMock()
        mock_dataloader.load = AsyncMock(return_value=[mock_user1, mock_user2])
        info.context.owasp_dataloaders = {NEW_USERS_BY_SNAPSHOT_ID: mock_dataloader}

        result = await resolver(None, mock_snapshot, info)

        mock_dataloader.load.assert_called_once_with(mock_snapshot.pk)
        assert result == [mock_user1, mock_user2]
