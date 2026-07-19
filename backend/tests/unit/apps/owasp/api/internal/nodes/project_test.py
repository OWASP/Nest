"""Test cases for ProjectNode."""

from unittest.mock import AsyncMock, Mock

import pytest

from apps.github.api.internal.dataloaders.issue import (
    ISSUES_COUNT_BY_PROJECT_ID,
    OPEN_ISSUES_COUNT_BY_PROJECT_ID,
    RECENT_ISSUES_BY_PROJECT_ID,
)
from apps.github.api.internal.dataloaders.milestone import RECENT_MILESTONES_BY_PROJECT_ID
from apps.github.api.internal.dataloaders.pull_request import (
    RECENT_PULL_REQUESTS_BY_PROJECT_ID,
)
from apps.github.api.internal.dataloaders.release import RECENT_RELEASES_BY_PROJECT_ID
from apps.github.api.internal.dataloaders.repository import (
    REPOSITORIES_BY_PROJECT_ID,
    REPOSITORIES_COUNT_BY_PROJECT_ID,
)
from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.repository import RepositoryNode
from apps.owasp.api.internal.dataloaders.project import (
    HEALTH_METRICS_LATEST_BY_PROJECT_ID,
    HEALTH_METRICS_LIST_BY_PROJECT_ID,
)
from apps.owasp.api.internal.nodes.project import (
    RECENT_ISSUES_LIMIT,
    RECENT_PULL_REQUESTS_LIMIT,
    RECENT_RELEASES_LIMIT,
    ProjectNode,
)
from apps.owasp.api.internal.nodes.project_health_metrics import ProjectHealthMetricsNode
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestProjectNode(GraphQLNodeBaseTest):
    def test_project_node_inheritance(self):
        assert hasattr(ProjectNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {field.name for field in ProjectNode.__strawberry_definition__.fields}
        expected_field_names = {
            "contribution_data",
            "contribution_stats",
            "contributors_count",
            "created_at",
            "forks_count",
            "is_active",
            "issues_count",
            "key",
            "languages",
            "level",
            "name",
            "open_issues_count",
            "recent_issues",
            "recent_milestones",
            "recent_pull_requests",
            "recent_releases",
            "repositories_count",
            "repositories",
            "stars_count",
            "summary",
            "topics",
            "type",
        }
        assert expected_field_names.issubset(field_names)

    def test_resolve_health_metrics_latest(self):
        field = self._get_field_by_name("health_metrics_latest", ProjectNode)
        assert field is not None
        assert field.type.of_type is ProjectHealthMetricsNode

    def test_resolve_health_metrics_list(self):
        field = self._get_field_by_name("health_metrics_list", ProjectNode)
        assert field is not None
        assert field.type.of_type is ProjectHealthMetricsNode

    def test_resolve_issues_count(self):
        field = self._get_field_by_name("issues_count", ProjectNode)
        assert field is not None
        assert field.type is int

    def test_resolve_key(self):
        field = self._get_field_by_name("key", ProjectNode)
        assert field is not None
        assert field.type is str

    def test_resolve_languages(self):
        field = self._get_field_by_name("languages", ProjectNode)
        assert field is not None
        assert field.type == list[str]

    def test_resolve_open_issues_count(self):
        field = self._get_field_by_name("open_issues_count", ProjectNode)
        assert field is not None
        assert field.type is int

    def test_resolve_recent_issues(self):
        field = self._get_field_by_name("recent_issues", ProjectNode)
        assert field is not None
        assert field.type.of_type is IssueNode

    def test_resolve_recent_milestones(self):
        field = self._get_field_by_name("recent_milestones", ProjectNode)
        assert field is not None
        assert field.type.of_type is MilestoneNode

    def test_resolve_recent_pull_requests(self):
        field = self._get_field_by_name("recent_pull_requests", ProjectNode)
        assert field is not None
        assert field.type.of_type is PullRequestNode

    def test_resolve_recent_releases(self):
        field = self._get_field_by_name("recent_releases", ProjectNode)
        assert field is not None
        assert field.type.of_type is ReleaseNode

    def test_resolve_repositories(self):
        field = self._get_field_by_name("repositories", ProjectNode)
        assert field is not None
        assert field.type.of_type is RepositoryNode

    def test_resolve_repositories_count(self):
        field = self._get_field_by_name("repositories_count", ProjectNode)
        assert field is not None
        assert field.type is int

    def test_resolve_topics(self):
        field = self._get_field_by_name("topics", ProjectNode)
        assert field is not None
        assert field.type == list[str]

    def test_resolve_contribution_stats(self):
        field = self._get_field_by_name("contribution_stats", ProjectNode)
        assert field is not None
        assert field.type.__class__.__name__ == "StrawberryOptional"

    def test_resolve_contribution_data(self):
        field = self._get_field_by_name("contribution_data", ProjectNode)
        assert field is not None
        assert field.type.__class__.__name__ == "StrawberryOptional"

    def test_contribution_stats_transforms_snake_case_to_camel_case(self):
        """Test that contribution_stats resolver transforms snake_case keys to camelCase."""
        mock_project = Mock()
        mock_project.contribution_stats = {
            "commits": 100,
            "issues": 25,
            "pull_requests": 50,
            "releases": 10,
            "total": 185,
        }

        instance = type("BoundNode", (), {})()
        instance.contribution_stats = mock_project.contribution_stats

        field = self._get_field_by_name("contribution_stats", ProjectNode)
        result = field.base_resolver.wrapped_func(None, instance)

        assert result is not None
        assert result["commits"] == 100
        assert result["pullRequests"] == 50
        assert result["issues"] == 25
        assert result["releases"] == 10
        assert result["total"] == 185
        assert "pull_requests" not in result


class TestProjectNodeResolvers:
    """Test ProjectNode resolver execution."""

    def _get_resolver(self, field_name):
        """Get the resolver function for a field."""
        for field in ProjectNode.__strawberry_definition__.fields:
            if field.name == field_name:
                return field.base_resolver.wrapped_func if field.base_resolver else None
        return None

    def _build_info(self, *, github=None, owasp=None):
        """Build a mock Info with dataloader mappings."""
        mock_info = Mock()
        mock_info.context.github_dataloaders = github or {}
        mock_info.context.owasp_dataloaders = owasp or {}
        return mock_info

    @pytest.mark.asyncio
    async def test_issues_count(self):
        """Test issues_count resolver delegates to the dataloader with pk."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=42)
        mock_info = self._build_info(github={ISSUES_COUNT_BY_PROJECT_ID: mock_loader})

        mock_project = Mock()
        mock_project.pk = 8

        resolver = self._get_resolver("issues_count")
        result = await resolver(None, mock_project, mock_info)

        assert result == 42
        mock_loader.load.assert_awaited_once_with(8)

    def test_key(self):
        """Test key resolver returns idx_key."""
        resolver = self._get_resolver("key")
        mock_project = Mock()
        mock_project.idx_key = "test-project"

        result = resolver(None, mock_project)

        assert result == "test-project"

    def test_languages(self):
        """Test languages resolver returns idx_languages."""
        resolver = self._get_resolver("languages")
        mock_project = Mock()
        mock_project.idx_languages = ["Python", "JavaScript"]

        result = resolver(None, mock_project)

        assert result == ["Python", "JavaScript"]

    def test_topics(self):
        """Test topics resolver returns idx_topics."""
        resolver = self._get_resolver("topics")
        mock_project = Mock()
        mock_project.idx_topics = ["security", "owasp"]

        result = resolver(None, mock_project)

        assert result == ["security", "owasp"]

    @pytest.mark.asyncio
    async def test_health_metrics_list_invalid_limit(self):
        """health_metrics_list returns empty list for invalid limit (no loader call)."""
        resolver = self._get_resolver("health_metrics_list")
        mock_project = Mock()
        mock_info = self._build_info()

        result = await resolver(None, mock_project, mock_info, limit=0)
        assert result == []

        result = await resolver(None, mock_project, mock_info, limit=-5)
        assert result == []

    @pytest.mark.asyncio
    async def test_health_metrics_list_loads_via_dataloader(self):
        """health_metrics_list delegates to the dataloader with (pk, limit)."""
        mock_metrics = [Mock(), Mock()]
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_metrics)
        mock_info = self._build_info(owasp={HEALTH_METRICS_LIST_BY_PROJECT_ID: mock_loader})

        mock_project = Mock()
        mock_project.pk = 7

        resolver = self._get_resolver("health_metrics_list")
        result = await resolver(None, mock_project, mock_info, limit=10)

        assert result == mock_metrics
        mock_loader.load.assert_awaited_once_with((7, 10))

    @pytest.mark.asyncio
    async def test_health_metrics_latest_loads_via_dataloader(self):
        """health_metrics_latest delegates to the dataloader with pk."""
        mock_metric = Mock()
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_metric)
        mock_info = self._build_info(owasp={HEALTH_METRICS_LATEST_BY_PROJECT_ID: mock_loader})

        mock_project = Mock()
        mock_project.pk = 9

        resolver = self._get_resolver("health_metrics_latest")
        result = await resolver(None, mock_project, mock_info)

        assert result == mock_metric
        mock_loader.load.assert_awaited_once_with(9)

    @pytest.mark.asyncio
    async def test_health_metrics_latest_none(self):
        """health_metrics_latest passes through None from the loader."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=None)
        mock_info = self._build_info(owasp={HEALTH_METRICS_LATEST_BY_PROJECT_ID: mock_loader})

        mock_project = Mock()
        mock_project.pk = 11

        resolver = self._get_resolver("health_metrics_latest")
        result = await resolver(None, mock_project, mock_info)

        assert result is None

    @pytest.mark.asyncio
    async def test_open_issues_count_loads_via_dataloader(self):
        """open_issues_count delegates to the dataloader with pk."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=37)
        mock_info = self._build_info(github={OPEN_ISSUES_COUNT_BY_PROJECT_ID: mock_loader})

        mock_project = Mock()
        mock_project.pk = 3

        resolver = self._get_resolver("open_issues_count")
        result = await resolver(None, mock_project, mock_info)

        assert result == 37
        mock_loader.load.assert_awaited_once_with(3)

    @pytest.mark.asyncio
    async def test_repositories_count_loads_via_dataloader(self):
        """repositories_count delegates to the dataloader with pk."""
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=5)
        mock_info = self._build_info(github={REPOSITORIES_COUNT_BY_PROJECT_ID: mock_loader})

        mock_project = Mock()
        mock_project.pk = 4

        resolver = self._get_resolver("repositories_count")
        result = await resolver(None, mock_project, mock_info)

        assert result == 5
        mock_loader.load.assert_awaited_once_with(4)

    @pytest.mark.asyncio
    async def test_recent_issues_loads_via_dataloader(self):
        """Recent issues delegate to the dataloader with (pk, RECENT_ISSUES_LIMIT)."""
        mock_issues = [Mock(), Mock()]
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_issues)
        mock_info = self._build_info(github={RECENT_ISSUES_BY_PROJECT_ID: mock_loader})

        mock_project = Mock()
        mock_project.pk = 1

        resolver = self._get_resolver("recent_issues")
        result = await resolver(None, mock_project, mock_info)

        assert result == mock_issues
        mock_loader.load.assert_awaited_once_with((1, RECENT_ISSUES_LIMIT))

    @pytest.mark.asyncio
    async def test_recent_milestones_invalid_limit(self):
        """recent_milestones returns empty list for invalid limit (no loader call)."""
        resolver = self._get_resolver("recent_milestones")
        mock_project = Mock()
        mock_info = self._build_info()

        result = await resolver(None, mock_project, mock_info, limit=0)
        assert result == []

    @pytest.mark.asyncio
    async def test_recent_milestones_loads_via_dataloader(self):
        """recent_milestones delegates to the dataloader with (pk, limit)."""
        mock_milestones = [Mock(), Mock()]
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_milestones)
        mock_info = self._build_info(github={RECENT_MILESTONES_BY_PROJECT_ID: mock_loader})

        mock_project = Mock()
        mock_project.pk = 1

        resolver = self._get_resolver("recent_milestones")
        result = await resolver(None, mock_project, mock_info, limit=5)

        assert result == mock_milestones
        mock_loader.load.assert_awaited_once_with((1, 5))

    @pytest.mark.asyncio
    async def test_recent_pull_requests_loads_via_dataloader(self):
        """Recent pull requests delegate to the dataloader with (pk, limit)."""
        mock_prs = [Mock(), Mock()]
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_prs)
        mock_info = self._build_info(github={RECENT_PULL_REQUESTS_BY_PROJECT_ID: mock_loader})

        mock_project = Mock()
        mock_project.pk = 1

        resolver = self._get_resolver("recent_pull_requests")
        result = await resolver(None, mock_project, mock_info)

        assert result == mock_prs
        mock_loader.load.assert_awaited_once_with((1, RECENT_PULL_REQUESTS_LIMIT))

    @pytest.mark.asyncio
    async def test_recent_releases_loads_via_dataloader(self):
        """Recent releases delegate to the dataloader with (pk, limit)."""
        mock_releases = [Mock(), Mock()]
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_releases)
        mock_info = self._build_info(github={RECENT_RELEASES_BY_PROJECT_ID: mock_loader})

        mock_project = Mock()
        mock_project.pk = 1

        resolver = self._get_resolver("recent_releases")
        result = await resolver(None, mock_project, mock_info)

        assert result == mock_releases
        mock_loader.load.assert_awaited_once_with((1, RECENT_RELEASES_LIMIT))

    @pytest.mark.asyncio
    async def test_repositories_loads_via_dataloader(self):
        """Repositories delegates to the dataloader with pk."""
        mock_repos = [Mock(), Mock()]
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=mock_repos)
        mock_info = self._build_info(github={REPOSITORIES_BY_PROJECT_ID: mock_loader})

        mock_project = Mock()
        mock_project.pk = 1

        resolver = self._get_resolver("repositories")
        result = await resolver(None, mock_project, mock_info)

        assert result == mock_repos
        mock_loader.load.assert_awaited_once_with(1)
