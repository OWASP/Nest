"""Tests for MemberSnapshot GraphQL node."""

from unittest.mock import AsyncMock, Mock

import pytest

from apps.owasp.api.internal.dataloaders.member_snapshot import (
    COMMITS_COUNT_BY_SNAPSHOT_ID_LOADER,
    ISSUES_COUNT_BY_SNAPSHOT_ID_LOADER,
    MESSAGES_COUNT_BY_SNAPSHOT_ID_LOADER,
    PULL_REQUESTS_COUNT_BY_SNAPSHOT_ID_LOADER,
    TOTAL_CONTRIBUTIONS_BY_SNAPSHOT_ID_LOADER,
)
from apps.owasp.api.internal.nodes.member_snapshot import MemberSnapshotNode
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestMemberSnapshotNode(GraphQLNodeBaseTest):
    def test_node_fields(self):
        mock_snapshot = Mock()
        mock_snapshot.start_at = "2025-01-01"
        mock_snapshot.end_at = "2025-10-01"
        mock_snapshot.contribution_heatmap_data = {"2025-01-15": 5}

        node = MemberSnapshotNode.__strawberry_definition__

        field_names = {field.name for field in node.fields}

        assert "start_at" in field_names
        assert "end_at" in field_names
        assert "contribution_heatmap_data" in field_names
        assert "github_user" in field_names
        assert "commits_count" in field_names
        assert "pull_requests_count" in field_names
        assert "issues_count" in field_names
        assert "messages_count" in field_names
        assert "total_contributions" in field_names

    @pytest.mark.asyncio
    async def test_commits_count_resolver(self):
        """Test commits_count returns count from dataloader."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=42)
        mock_info = Mock()
        mock_info.context.owasp_dataloaders = {COMMITS_COUNT_BY_SNAPSHOT_ID_LOADER: mock_loader}

        mock_snapshot = Mock()
        mock_snapshot.pk = 1

        field = self._get_field_by_name("commits_count", MemberSnapshotNode)
        result = await field.base_resolver.wrapped_func(None, mock_snapshot, mock_info)

        assert result == 42
        mock_loader.load.assert_awaited_once_with(1)

    def test_github_user_resolver(self):
        """Test github_user returns user from snapshot."""
        mock_user = Mock()
        mock_snapshot = Mock()
        mock_snapshot.github_user = mock_user

        field = self._get_field_by_name("github_user", MemberSnapshotNode)
        result = field.base_resolver.wrapped_func(None, mock_snapshot)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_issues_count_resolver(self):
        """Test issues_count returns count from dataloader."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=15)
        mock_info = Mock()
        mock_info.context.owasp_dataloaders = {ISSUES_COUNT_BY_SNAPSHOT_ID_LOADER: mock_loader}

        mock_snapshot = Mock()
        mock_snapshot.pk = 1

        field = self._get_field_by_name("issues_count", MemberSnapshotNode)
        result = await field.base_resolver.wrapped_func(None, mock_snapshot, mock_info)

        assert result == 15
        mock_loader.load.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_pull_requests_count_resolver(self):
        """Test pull_requests_count returns count from dataloader."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=23)
        mock_info = Mock()
        mock_info.context.owasp_dataloaders = {
            PULL_REQUESTS_COUNT_BY_SNAPSHOT_ID_LOADER: mock_loader
        }

        mock_snapshot = Mock()
        mock_snapshot.pk = 1

        field = self._get_field_by_name("pull_requests_count", MemberSnapshotNode)
        result = await field.base_resolver.wrapped_func(None, mock_snapshot, mock_info)

        assert result == 23
        mock_loader.load.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_messages_count_resolver(self):
        """Test messages_count returns count from dataloader."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=100)
        mock_info = Mock()
        mock_info.context.owasp_dataloaders = {MESSAGES_COUNT_BY_SNAPSHOT_ID_LOADER: mock_loader}

        mock_snapshot = Mock()
        mock_snapshot.pk = 1

        field = self._get_field_by_name("messages_count", MemberSnapshotNode)
        result = await field.base_resolver.wrapped_func(None, mock_snapshot, mock_info)

        assert result == 100
        mock_loader.load.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_total_contributions_resolver(self):
        """Test total_contributions returns total from dataloader."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=80)
        mock_info = Mock()
        mock_info.context.owasp_dataloaders = {
            TOTAL_CONTRIBUTIONS_BY_SNAPSHOT_ID_LOADER: mock_loader
        }

        mock_snapshot = Mock()
        mock_snapshot.pk = 1

        field = self._get_field_by_name("total_contributions", MemberSnapshotNode)
        result = await field.base_resolver.wrapped_func(None, mock_snapshot, mock_info)

        assert result == 80
        mock_loader.load.assert_awaited_once_with(1)
