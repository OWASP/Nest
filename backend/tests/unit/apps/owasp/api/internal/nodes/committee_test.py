"""Tests for Committee GraphQL node."""

import inspect
import math
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from apps.github.api.internal.dataloaders.repository_contributor import (
    TOP_CONTRIBUTORS_BY_COMMITTEE_ID_LOADER,
)
from apps.github.api.internal.nodes.repository_contributor import RepositoryContributorNode
from apps.owasp.api.internal.dataloaders.committee import (
    ENTITY_CHANNELS_BY_COMMITTEE_ID_LOADER,
    ENTITY_LEADERS_BY_COMMITTEE_ID_LOADER,
)
from apps.owasp.api.internal.nodes.committee import CommitteeNode
from apps.owasp.models.committee import Committee
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestCommitteeNode(GraphQLNodeBaseTest):
    def test_contributors_count_resolver(self):
        """Test contributors_count returns count from repository."""
        mock_repo = Mock()
        mock_repo.contributors_count = 42

        mock_committee = Mock()
        mock_committee.owasp_repository = mock_repo

        field = self._get_field_by_name("contributors_count", CommitteeNode)
        result = field.base_resolver.wrapped_func(None, mock_committee)

        assert result == 42

    def test_created_at_resolver(self):
        """Test created_at returns indexed timestamp."""
        mock_committee = Mock()
        mock_committee.idx_created_at = 1234567890.0

        field = self._get_field_by_name("created_at", CommitteeNode)
        result = field.base_resolver.wrapped_func(None, mock_committee)

        assert math.isclose(result, 1234567890.0)

    def test_forks_count_resolver(self):
        """Test forks_count returns count from repository."""
        mock_repo = Mock()
        mock_repo.forks_count = 15

        mock_committee = Mock()
        mock_committee.owasp_repository = mock_repo

        field = self._get_field_by_name("forks_count", CommitteeNode)
        result = field.base_resolver.wrapped_func(None, mock_committee)

        assert result == 15

    def test_issues_count_resolver(self):
        """Test issues_count returns open issues from repository."""
        mock_repo = Mock()
        mock_repo.open_issues_count = 23

        mock_committee = Mock()
        mock_committee.owasp_repository = mock_repo

        field = self._get_field_by_name("issues_count", CommitteeNode)
        result = field.base_resolver.wrapped_func(None, mock_committee)

        assert result == 23

    def test_repositories_count_resolver(self):
        """Test repositories_count always returns 1 for committees."""
        mock_committee = Mock()

        field = self._get_field_by_name("repositories_count", CommitteeNode)
        result = field.base_resolver.wrapped_func(None, mock_committee)

        assert result == 1

    def test_stars_count_resolver(self):
        """Test stars_count returns count from repository."""
        mock_repo = Mock()
        mock_repo.stars_count = 100

        mock_committee = Mock()
        mock_committee.owasp_repository = mock_repo

        field = self._get_field_by_name("stars_count", CommitteeNode)
        result = field.base_resolver.wrapped_func(None, mock_committee)

        assert result == 100

    def test_top_contributors_field_definition(self):
        """top_contributors field is defined and returns RepositoryContributorNode list."""
        field = self._get_field_by_name("top_contributors", CommitteeNode)
        assert field is not None
        assert field.type.of_type is RepositoryContributorNode


class TestCommitteeNodeResolvers:
    """Test CommitteeNode resolver execution."""

    def _get_resolver(self, field_name):
        """Get the resolver function for a field."""
        for field in CommitteeNode.__strawberry_definition__.fields:
            if field.name == field_name:
                return field.base_resolver.wrapped_func if field.base_resolver else None
        return None

    def _build_info(self, *, owasp=None, github=None):
        """Build a mock Info with dataloader mappings."""
        mock_info = Mock()
        mock_info.context.owasp_dataloaders = owasp or {}
        mock_info.context.github_dataloaders = github or {}
        return mock_info

    @pytest.mark.asyncio
    async def test_entity_channels_loads_via_dataloader(self):
        """entity_channels delegates to the dataloader with pk."""
        mock_channels = [Mock(), Mock()]
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_channels)
        mock_info = self._build_info(owasp={ENTITY_CHANNELS_BY_COMMITTEE_ID_LOADER: mock_loader})

        mock_committee = Mock()
        mock_committee.pk = 1

        resolver = self._get_resolver("entity_channels")
        result = await resolver(None, mock_committee, mock_info)

        assert result == mock_channels
        mock_loader.load.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_entity_channels_overrides_generic_entity_node(self):
        """CommitteeNode.entity_channels is the async dataloader resolver, not the sync base."""
        resolver = self._get_resolver("entity_channels")
        assert inspect.iscoroutinefunction(resolver)

    @pytest.mark.asyncio
    async def test_entity_leaders_loads_via_dataloader(self):
        """entity_leaders delegates to the dataloader with pk."""
        mock_leaders = [Mock(), Mock()]
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_leaders)
        mock_info = self._build_info(owasp={ENTITY_LEADERS_BY_COMMITTEE_ID_LOADER: mock_loader})

        mock_committee = Mock()
        mock_committee.pk = 1

        resolver = self._get_resolver("entity_leaders")
        assert inspect.iscoroutinefunction(resolver)
        result = await resolver(None, mock_committee, mock_info)

        assert result == mock_leaders
        mock_loader.load.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_top_contributors_overrides_generic_entity_node(self):
        """CommitteeNode.top_contributors is the async dataloader resolver, not the sync base."""
        resolver = self._get_resolver("top_contributors")
        assert inspect.iscoroutinefunction(resolver)

    @pytest.mark.asyncio
    async def test_top_contributors_loads_via_dataloader(self):
        """top_contributors delegates to the dataloader and returns RepositoryContributorNodes."""
        mock_contributors = [
            {
                "avatar_url": "url1",
                "contributions_count": 100,
                "id": "user1",
                "login": "user1",
                "name": "User 1",
            },
            {
                "avatar_url": "url2",
                "contributions_count": 50,
                "id": "user2",
                "login": "user2",
                "name": "User 2",
            },
        ]
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_contributors)
        mock_info = self._build_info(github={TOP_CONTRIBUTORS_BY_COMMITTEE_ID_LOADER: mock_loader})

        mock_committee = MagicMock(spec=Committee)
        mock_committee.pk = 7

        resolver = self._get_resolver("top_contributors")
        result = await resolver(None, mock_committee, mock_info)

        mock_loader.load.assert_awaited_once_with(mock_committee.pk)
        assert len(result) == 2
        assert all(isinstance(c, RepositoryContributorNode) for c in result)
        assert result[0].login == "user1"
        assert result[1].login == "user2"
