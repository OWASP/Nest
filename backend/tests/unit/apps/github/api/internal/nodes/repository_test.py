"""Test cases for RepositoryNode."""

from unittest.mock import AsyncMock, Mock

import pytest

from apps.github.api.internal.dataloaders.issue import ISSUES_BY_REPOSITORY_ID_LOADER
from apps.github.api.internal.dataloaders.milestone import (
    RECENT_MILESTONES_BY_REPOSITORY_ID_LOADER,
)
from apps.github.api.internal.dataloaders.release import (
    LATEST_RELEASE_BY_REPOSITORY_ID_LOADER,
    RECENT_RELEASES_BY_REPOSITORY_ID_LOADER,
)
from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.api.internal.nodes.organization import OrganizationNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.repository import RepositoryNode
from apps.github.api.internal.nodes.repository_contributor import RepositoryContributorNode
from apps.owasp.api.internal.dataloaders.project import PROJECT_BY_REPOSITORY_ID_LOADER
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestRepositoryNode(GraphQLNodeBaseTest):
    def test_repository_node_inheritance(self):
        assert hasattr(RepositoryNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {field.name for field in RepositoryNode.__strawberry_definition__.fields}
        expected_field_names = {
            "_id",
            "commits_count",
            "contributors_count",
            "created_at",
            "description",
            "forks_count",
            "is_archived",
            "issues",
            "key",
            "languages",
            "latest_release",
            "license",
            "name",
            "open_issues_count",
            "organization",
            "project",
            "recent_milestones",
            "releases",
            "size",
            "stars_count",
            "subscribers_count",
            "top_contributors",
            "topics",
            "updated_at",
            "url",
        }
        assert expected_field_names.issubset(field_names)

    def test_resolve_issues(self):
        field = self._get_field_by_name("issues", RepositoryNode)
        assert field is not None
        assert field.type.of_type is IssueNode

    def test_resolve_languages(self):
        field = self._get_field_by_name("languages", RepositoryNode)
        assert field is not None
        assert field.type == list[str]

    def test_resolve_latest_release(self):
        field = self._get_field_by_name("latest_release", RepositoryNode)
        assert field is not None
        assert field.type.of_type is str

    def test_resolve_organization(self):
        field = self._get_field_by_name("organization", RepositoryNode)
        assert field is not None
        assert field.type.of_type is OrganizationNode

    def test_resolve_recent_milestones(self):
        field = self._get_field_by_name("recent_milestones", RepositoryNode)
        assert field is not None
        assert field.type.of_type is MilestoneNode

    def test_resolve_releases(self):
        field = self._get_field_by_name("releases", RepositoryNode)
        assert field is not None
        assert field.type.of_type is ReleaseNode

    def test_resolve_top_contributors(self):
        field = self._get_field_by_name("top_contributors", RepositoryNode)
        assert field is not None
        assert field.type.of_type is RepositoryContributorNode

    def test_resolve_topics(self):
        field = self._get_field_by_name("topics", RepositoryNode)
        assert field is not None
        assert field.type == list[str]

    def test_resolve_url(self):
        field = self._get_field_by_name("url", RepositoryNode)
        assert field is not None
        assert field.type is str

    @pytest.mark.asyncio
    async def test_issues_method(self):
        """Test issues async resolution via dataloader."""
        mock_issues = [Mock(), Mock()]
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_issues)
        mock_info = Mock()
        mock_info.context.github_dataloaders = {ISSUES_BY_REPOSITORY_ID_LOADER: mock_loader}

        mock_repository = Mock()
        mock_repository.pk = 1

        field = self._get_field_by_name("issues", RepositoryNode)
        result = await field.base_resolver.wrapped_func(None, mock_repository, mock_info)

        assert result == mock_issues
        mock_loader.load.assert_awaited_once_with(1)

    def test_languages_method(self):
        """Test languages method resolution."""
        mock_repository = Mock()
        mock_repository.languages = {"Python": 1000, "JavaScript": 500}

        field = self._get_field_by_name("languages", RepositoryNode)
        result = field.base_resolver.wrapped_func(None, mock_repository)
        assert result == ["Python", "JavaScript"]

    @pytest.mark.asyncio
    async def test_latest_release_method(self):
        """Test latest_release async resolution via dataloader."""
        mock_release = Mock()
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_release)
        mock_info = Mock()
        mock_info.context.github_dataloaders = {
            LATEST_RELEASE_BY_REPOSITORY_ID_LOADER: mock_loader
        }

        mock_repository = Mock()
        mock_repository.pk = 1

        field = self._get_field_by_name("latest_release", RepositoryNode)
        result = await field.base_resolver.wrapped_func(None, mock_repository, mock_info)

        assert result == mock_release
        mock_loader.load.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_project_method(self):
        """Test project async resolution via dataloader."""
        mock_project = Mock()
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_project)
        mock_info = Mock()
        mock_info.context.owasp_dataloaders = {PROJECT_BY_REPOSITORY_ID_LOADER: mock_loader}

        mock_repository = Mock()
        mock_repository.pk = 1

        field = self._get_field_by_name("project", RepositoryNode)
        result = await field.base_resolver.wrapped_func(None, mock_repository, mock_info)

        assert result == mock_project
        mock_loader.load.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_recent_milestones_method(self):
        """Test recent_milestones async resolution via dataloader."""
        mock_milestones = [Mock(), Mock()]
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_milestones)
        mock_info = Mock()
        mock_info.context.github_dataloaders = {
            RECENT_MILESTONES_BY_REPOSITORY_ID_LOADER: mock_loader
        }

        mock_repository = Mock()
        mock_repository.pk = 1

        field = self._get_field_by_name("recent_milestones", RepositoryNode)
        result = await field.base_resolver.wrapped_func(None, mock_repository, mock_info)

        assert result == mock_milestones
        mock_loader.load.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_releases_method(self):
        """Test releases async resolution via dataloader."""
        mock_releases = [Mock(), Mock()]
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_releases)
        mock_info = Mock()
        mock_info.context.github_dataloaders = {
            RECENT_RELEASES_BY_REPOSITORY_ID_LOADER: mock_loader
        }

        mock_repository = Mock()
        mock_repository.pk = 1

        field = self._get_field_by_name("releases", RepositoryNode)
        result = await field.base_resolver.wrapped_func(None, mock_repository, mock_info)

        assert result == mock_releases
        mock_loader.load.assert_awaited_once_with(1)

    def test_top_contributors_method(self):
        """Test top_contributors method resolution."""
        mock_repository = Mock()
        mock_repository.idx_top_contributors = [
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

        field = self._get_field_by_name("top_contributors", RepositoryNode)
        result = field.base_resolver.wrapped_func(None, mock_repository)
        assert len(result) == 2
        assert all(isinstance(c, RepositoryContributorNode) for c in result)

    def test_topics_method(self):
        """Test topics method resolution."""
        mock_repository = Mock()
        mock_repository.topics = ["security", "python", "django"]

        field = self._get_field_by_name("topics", RepositoryNode)
        result = field.base_resolver.wrapped_func(None, mock_repository)
        assert result == ["security", "python", "django"]

    def test_url_method(self):
        """Test url method resolution."""
        mock_repository = Mock()
        mock_repository.url = "https://github.com/test-org/test-repo"

        field = self._get_field_by_name("url", RepositoryNode)
        result = field.base_resolver.wrapped_func(None, mock_repository)
        assert result == "https://github.com/test-org/test-repo"

    def test_is_archived_field_exists(self):
        """Test that is_archived field is exposed in the GraphQL schema."""
        field_names = {field.name for field in RepositoryNode.__strawberry_definition__.fields}
        assert "is_archived" in field_names, (
            "is_archived field should be exposed in RepositoryNode"
        )

    def test_resolve_is_archived(self):
        """Test is_archived field type."""
        field = self._get_field_by_name("is_archived", RepositoryNode)
        assert field is not None
        assert field.type is bool
