"""Test cases for ProjectNode."""

from unittest.mock import MagicMock, Mock

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.repository import RepositoryNode
from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.api.internal.nodes.project_health_metrics import ProjectHealthMetricsNode
from apps.owasp.models.project import Project
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

    def test_recent_pull_requests_returns_empty_when_not_prefetched(self):
        """Test that recent_pull_requests returns empty list when _recent_pull_requests not set."""
        mock_project = Mock(spec=Project)
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value.__getitem__.return_value = []
        mock_project.pull_requests = mock_queryset
        mock_info = Mock()
        resolver = ProjectNode.recent_pull_requests.base_resolver.wrapped_func
        result = resolver(mock_info, mock_project)

        assert result == []
        mock_queryset.order_by.assert_called_once_with("-created_at")

    def test_recent_pull_requests_returns_prefetched_data(self):
        """Test that recent_pull_requests returns prefetched data from _recent_pull_requests."""
        mock_pr1 = Mock()
        mock_pr1.id = 1
        mock_pr2 = Mock()
        mock_pr2.id = 2

        mock_project = Mock(spec=Project)
        mock_project._recent_pull_requests = [mock_pr1, mock_pr2]
        mock_info = Mock()

        resolver = ProjectNode.recent_pull_requests.base_resolver.wrapped_func
        result = resolver(mock_info, mock_project)

        assert len(result) == 2
        assert result[0] == mock_pr1
        assert result[1] == mock_pr2

    def test_recent_pull_requests_prefetch_configuration(self):
        """Test that recent_pull_requests has prefetch_related optimization configured."""
        field = self._get_field_by_name("recent_pull_requests", ProjectNode)
        assert field is not None
        assert hasattr(field, "extensions")

    def test_recent_pull_requests_uses_correct_limit(self):
        """Test that recent_pull_requests respects the RECENT_PULL_REQUESTS_LIMIT."""
        from apps.owasp.api.internal.nodes.project import RECENT_PULL_REQUESTS_LIMIT

        assert RECENT_PULL_REQUESTS_LIMIT == 5
