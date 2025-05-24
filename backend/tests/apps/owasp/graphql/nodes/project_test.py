"""Test cases for ProjectNode."""

from apps.owasp.graphql.nodes.project import ProjectNode


class TestProjectNode:
    def test_project_node_inheritance(self):
        assert hasattr(ProjectNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {field.name for field in ProjectNode.__strawberry_definition__.fields}
        expected_field_names = {
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

    def test_resolve_issues_count(self):
        field = self._get_field_by_name("issues_count")
        assert field is not None
        assert "int" in str(field.type).lower()

    def test_resolve_key(self):
        field = self._get_field_by_name("key")
        assert field is not None
        assert "str" in str(field.type).lower()

    def test_resolve_languages(self):
        field = self._get_field_by_name("languages")
        assert field is not None
        assert "str" in str(field.type).lower()

    def test_resolve_recent_issues(self):
        field = self._get_field_by_name("recent_issues")
        assert field is not None
        inner_type = getattr(field.type, "of_type", None) or field.type
        assert "IssueNode" in str(inner_type)

    def test_resolve_recent_milestones(self):
        field = self._get_field_by_name("recent_milestones")
        assert field is not None
        inner_type = getattr(field.type, "of_type", None) or field.type
        assert "MilestoneNode" in str(inner_type)

    def test_resolve_recent_pull_requests(self):
        field = self._get_field_by_name("recent_pull_requests")
        assert field is not None
        inner_type = getattr(field.type, "of_type", None) or field.type
        assert "PullRequestNode" in str(inner_type)

    def test_resolve_recent_releases(self):
        field = self._get_field_by_name("recent_releases")
        assert field is not None
        inner_type = getattr(field.type, "of_type", None) or field.type
        assert "ReleaseNode" in str(inner_type)

    def test_resolve_repositories(self):
        field = self._get_field_by_name("repositories")
        assert field is not None
        inner_type = getattr(field.type, "of_type", None) or field.type
        assert "RepositoryNode" in str(inner_type)

    def test_resolve_repositories_count(self):
        field = self._get_field_by_name("repositories_count")
        assert field is not None
        assert "int" in str(field.type).lower()

    def test_resolve_topics(self):
        field = self._get_field_by_name("topics")
        assert field is not None
        assert "str" in str(field.type).lower()
