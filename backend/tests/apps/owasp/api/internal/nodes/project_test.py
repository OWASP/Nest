"""Test cases for ProjectNode."""

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.repository import RepositoryNode
from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.api.internal.nodes.project_health_metrics import ProjectHealthMetricsNode


class TestProjectNode:
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
            "level",
            "name",
            "open_issues_count",
            "stars_count",
            "summary",
            "type",
            "issues_count",
            "key",
            "languages",
            "recent_issues",
            "recent_milestones",
            "recent_pull_requests",
            "recent_releases",
            "repositories",
            "repositories_count",
            "topics",
        }
        assert expected_field_names.issubset(field_names)

    def _get_field_by_name(self, name):
        return next(
            (f for f in ProjectNode.__strawberry_definition__.fields if f.name == name), None
        )

    def test_resolve_health_metrics_latest(self):
        field = self._get_field_by_name("health_metrics_latest")
        assert field is not None
        assert field.type.of_type is ProjectHealthMetricsNode

    def test_resolve_health_metrics_list(self):
        field = self._get_field_by_name("health_metrics_list")
        assert field is not None
        assert field.type.of_type is ProjectHealthMetricsNode

    def test_resolve_issues_count(self):
        field = self._get_field_by_name("issues_count")
        assert field is not None
        assert field.type is int

    def test_resolve_key(self):
        field = self._get_field_by_name("key")
        assert field is not None
        assert field.type is str

    def test_resolve_languages(self):
        field = self._get_field_by_name("languages")
        assert field is not None
        assert field.type == list[str]

    def test_resolve_recent_issues(self):
        field = self._get_field_by_name("recent_issues")
        assert field is not None
        assert field.type.of_type is IssueNode

    def test_resolve_recent_milestones(self):
        field = self._get_field_by_name("recent_milestones")
        assert field is not None
        assert field.type.of_type is MilestoneNode

    def test_resolve_recent_pull_requests(self):
        field = self._get_field_by_name("recent_pull_requests")
        assert field is not None
        assert field.type.of_type is PullRequestNode

    def test_resolve_recent_releases(self):
        field = self._get_field_by_name("recent_releases")
        assert field is not None
        assert field.type.of_type is ReleaseNode

    def test_resolve_repositories(self):
        field = self._get_field_by_name("repositories")
        assert field is not None
        assert field.type.of_type is RepositoryNode

    def test_resolve_repositories_count(self):
        field = self._get_field_by_name("repositories_count")
        assert field is not None
        assert field.type is int

    def test_resolve_topics(self):
        field = self._get_field_by_name("topics")
        assert field is not None
        assert field.type == list[str]

    def test_resolve_contribution_stats(self):
        field = self._get_field_by_name("contribution_stats")
        assert field is not None
        assert field.type.__class__.__name__ == "ScalarWrapper"
