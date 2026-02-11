"""Test cases for ProjectNode."""

from unittest.mock import MagicMock, Mock

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.repository import RepositoryNode
from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.api.internal.nodes.project_health_metrics import ProjectHealthMetricsNode
from tests.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


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
        from unittest.mock import Mock

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

    def test_health_metrics_list_with_invalid_limit(self):
        """Test health_metrics_list returns empty list for invalid limit."""
        resolver = self._get_resolver("health_metrics_list")
        mock_project = MagicMock()

        result = resolver(None, mock_project, limit=0)
        assert result == []

        result = resolver(None, mock_project, limit=-5)
        assert result == []

    def test_health_metrics_list_with_valid_limit(self):
        """Test health_metrics_list returns metrics with valid limit."""
        resolver = self._get_resolver("health_metrics_list")
        mock_project = MagicMock()
        mock_metrics = [MagicMock(), MagicMock()]
        mock_sliced = MagicMock()
        mock_sliced.__reversed__ = lambda _: iter(mock_metrics)
        mock_project.health_metrics.order_by.return_value.__getitem__.return_value = mock_sliced

        result = resolver(None, mock_project, limit=10)

        mock_project.health_metrics.order_by.assert_called_once_with("-nest_created_at")
        assert result == mock_metrics

    def test_health_metrics_latest(self):
        """Test health_metrics_latest returns latest metric."""
        resolver = self._get_resolver("health_metrics_latest")
        mock_project = MagicMock()
        mock_latest = MagicMock()
        mock_project.health_metrics.order_by.return_value.first.return_value = mock_latest

        result = resolver(None, mock_project)

        mock_project.health_metrics.order_by.assert_called_once_with("-nest_created_at")
        assert result == mock_latest

    def test_health_metrics_latest_none(self):
        """Test health_metrics_latest returns None when no metrics."""
        resolver = self._get_resolver("health_metrics_latest")
        mock_project = MagicMock()
        mock_project.health_metrics.order_by.return_value.first.return_value = None

        result = resolver(None, mock_project)

        assert result is None

    def test_recent_milestones_with_invalid_limit(self):
        """Test recent_milestones returns empty list for invalid limit."""
        resolver = self._get_resolver("recent_milestones")
        mock_project = MagicMock()

        result = resolver(None, mock_project, limit=0)
        assert result == []

    def test_issues_count(self):
        """Test issues_count resolver returns idx_issues_count."""
        resolver = self._get_resolver("issues_count")
        mock_project = MagicMock()
        mock_project.idx_issues_count = 42

        result = resolver(None, mock_project)

        assert result == 42

    def test_key(self):
        """Test key resolver returns idx_key."""
        resolver = self._get_resolver("key")
        mock_project = MagicMock()
        mock_project.idx_key = "test-project"

        result = resolver(None, mock_project)

        assert result == "test-project"

    def test_languages(self):
        """Test languages resolver returns idx_languages."""
        resolver = self._get_resolver("languages")
        mock_project = MagicMock()
        mock_project.idx_languages = ["Python", "JavaScript"]

        result = resolver(None, mock_project)

        assert result == ["Python", "JavaScript"]

    def test_repositories_count(self):
        """Test repositories_count resolver returns idx_repositories_count."""
        resolver = self._get_resolver("repositories_count")
        mock_project = MagicMock()
        mock_project.idx_repositories_count = 5

        result = resolver(None, mock_project)

        assert result == 5

    def test_topics(self):
        """Test topics resolver returns idx_topics."""
        resolver = self._get_resolver("topics")
        mock_project = MagicMock()
        mock_project.idx_topics = ["security", "owasp"]

        result = resolver(None, mock_project)

        assert result == ["security", "owasp"]
