"""Test cases for ReleaseNode."""

from unittest.mock import AsyncMock, Mock

import pytest

from apps.github.api.internal.dataloaders.release import RELEASE_URL_BY_ID_LOADER
from apps.github.api.internal.dataloaders.repository import (
    REPOSITORY_BY_RELEASE_ID_LOADER,
    REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER,
)
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.user import UserNode
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestReleaseNode(GraphQLNodeBaseTest):
    """Test cases for ReleaseNode class."""

    def test_release_node_inheritance(self):
        assert hasattr(ReleaseNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {field.name for field in ReleaseNode.__strawberry_definition__.fields}
        expected_field_names = {
            "_id",
            "author",
            "is_pre_release",
            "name",
            "organization_name",
            "project_name",
            "published_at",
            "repository_name",
            "tag_name",
            "url",
        }
        assert field_names == expected_field_names

    def test_author_field(self):
        fields = ReleaseNode.__strawberry_definition__.fields
        author_field = next((field for field in fields if field.name == "author"), None)
        assert author_field is not None
        assert author_field.type.of_type is UserNode

    @pytest.mark.asyncio
    async def test_organization_name_with_organization(self):
        """Test organization_name field when organization exists."""
        mock_repo = Mock()
        mock_org = Mock()
        mock_org.login = "test-org"
        mock_repo.organization = mock_org

        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_repo)
        mock_info = Mock()
        mock_info.context.github_dataloaders = {REPOSITORY_BY_RELEASE_ID_LOADER: mock_loader}

        mock_release = Mock()
        mock_release.pk = 1

        field = self._get_field_by_name("organization_name", ReleaseNode)
        result = await field.base_resolver.wrapped_func(None, mock_release, mock_info)

        assert result == "test-org"
        mock_loader.load.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_organization_name_without_organization(self):
        """Test organization_name field when organization doesn't exist."""
        mock_repo = Mock()
        mock_repo.organization = None

        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_repo)
        mock_info = Mock()
        mock_info.context.github_dataloaders = {REPOSITORY_BY_RELEASE_ID_LOADER: mock_loader}

        mock_release = Mock()
        mock_release.pk = 1

        field = self._get_field_by_name("organization_name", ReleaseNode)
        result = await field.base_resolver.wrapped_func(None, mock_release, mock_info)

        assert result is None

    @pytest.mark.asyncio
    async def test_organization_name_without_repository(self):
        """Test organization_name field when repository doesn't exist."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=None)
        mock_info = Mock()
        mock_info.context.github_dataloaders = {REPOSITORY_BY_RELEASE_ID_LOADER: mock_loader}

        mock_release = Mock()
        mock_release.pk = 1

        field = self._get_field_by_name("organization_name", ReleaseNode)
        result = await field.base_resolver.wrapped_func(None, mock_release, mock_info)

        assert result is None

    @pytest.mark.asyncio
    async def test_project_name_with_project(self):
        """Test project_name field when project exists."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value="Test Project")
        mock_info = Mock()
        mock_info.context.github_dataloaders = {
            REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER: mock_loader
        }

        mock_release = Mock()
        mock_release.pk = 1

        field = self._get_field_by_name("project_name", ReleaseNode)
        result = await field.base_resolver.wrapped_func(None, mock_release, mock_info)

        assert result == "Test Project"
        mock_loader.load.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_project_name_returns_none(self):
        """Test project_name field returns None when dataloader returns None."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=None)
        mock_info = Mock()
        mock_info.context.github_dataloaders = {
            REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER: mock_loader
        }

        mock_release = Mock()
        mock_release.pk = 1

        field = self._get_field_by_name("project_name", ReleaseNode)
        result = await field.base_resolver.wrapped_func(None, mock_release, mock_info)

        assert result is None
        mock_loader.load.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_repository_name_with_repository(self):
        """Test repository_name field when repository exists."""
        mock_repo = Mock()
        mock_repo.name = "test-repo"

        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_repo)
        mock_info = Mock()
        mock_info.context.github_dataloaders = {REPOSITORY_BY_RELEASE_ID_LOADER: mock_loader}

        mock_release = Mock()
        mock_release.pk = 1

        field = self._get_field_by_name("repository_name", ReleaseNode)
        result = await field.base_resolver.wrapped_func(None, mock_release, mock_info)

        assert result == "test-repo"
        mock_loader.load.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_repository_name_without_repository(self):
        """Test repository_name field when repository doesn't exist."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=None)
        mock_info = Mock()
        mock_info.context.github_dataloaders = {REPOSITORY_BY_RELEASE_ID_LOADER: mock_loader}

        mock_release = Mock()
        mock_release.pk = 1

        field = self._get_field_by_name("repository_name", ReleaseNode)
        result = await field.base_resolver.wrapped_func(None, mock_release, mock_info)

        assert result is None

    @pytest.mark.asyncio
    async def test_url_field(self):
        """Test url field resolution via dataloader."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(
            return_value="https://github.com/test-org/test-repo/releases/tag/v1.0.0"
        )
        mock_info = Mock()
        mock_info.context.github_dataloaders = {RELEASE_URL_BY_ID_LOADER: mock_loader}

        mock_release = Mock()
        mock_release.pk = 1

        field = self._get_field_by_name("url", ReleaseNode)
        result = await field.base_resolver.wrapped_func(None, mock_release, mock_info)

        assert result == "https://github.com/test-org/test-repo/releases/tag/v1.0.0"
        mock_loader.load.assert_awaited_once_with(1)
