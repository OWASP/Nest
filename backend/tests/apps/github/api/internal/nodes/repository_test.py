"""Test cases for RepositoryNode."""

from unittest.mock import Mock

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.milestone import MilestoneNode
from apps.github.api.internal.nodes.organization import OrganizationNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.repository import RepositoryNode
from apps.github.api.internal.nodes.repository_contributor import RepositoryContributorNode


class TestRepositoryNode:
    def test_repository_node_inheritance(self):
        assert hasattr(RepositoryNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {field.name for field in RepositoryNode.__strawberry_definition__.fields}
        expected_field_names = {
            "commits_count",
            "contributors_count",
            "created_at",
            "description",
            "forks_count",
            "issues",
            "key",
            "languages",
            "latest_release",
            "license",
            "name",
            "open_issues_count",
            "organization",
            "owner_key",
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

    def _get_field_by_name(self, name):
        return next(
            (f for f in RepositoryNode.__strawberry_definition__.fields if f.name == name), None
        )

    def test_resolve_issues(self):
        field = self._get_field_by_name("issues")
        assert field is not None
        assert field.type.of_type is IssueNode

    def test_resolve_languages(self):
        field = self._get_field_by_name("languages")
        assert field is not None
        assert field.type == list[str]

    def test_resolve_latest_release(self):
        field = self._get_field_by_name("latest_release")
        assert field is not None
        assert field.type is str

    def test_resolve_organization(self):
        field = self._get_field_by_name("organization")
        assert field is not None
        assert field.type.of_type is OrganizationNode

    def test_resolve_owner_key(self):
        field = self._get_field_by_name("owner_key")
        assert field is not None
        assert field.type is str

    def test_resolve_recent_milestones(self):
        field = self._get_field_by_name("recent_milestones")
        assert field is not None
        assert field.type.of_type is MilestoneNode

    def test_resolve_releases(self):
        field = self._get_field_by_name("releases")
        assert field is not None
        assert field.type.of_type is ReleaseNode

    def test_resolve_top_contributors(self):
        field = self._get_field_by_name("top_contributors")
        assert field is not None
        assert field.type.of_type is RepositoryContributorNode

    def test_resolve_topics(self):
        field = self._get_field_by_name("topics")
        assert field is not None
        assert field.type == list[str]

    def test_resolve_url(self):
        field = self._get_field_by_name("url")
        assert field is not None
        assert field.type is str

    def test_issues_method(self):
        """Test issues method resolution."""
        mock_repository = Mock()
        mock_issues = Mock()
        mock_issues.select_related.return_value.order_by.return_value.__getitem__ = Mock(
            return_value=[]
        )
        mock_repository.issues = mock_issues

        RepositoryNode.issues(mock_repository)
        mock_issues.select_related.assert_called_with("author")
        mock_issues.select_related.return_value.order_by.assert_called_with("-created_at")

    def test_languages_method(self):
        """Test languages method resolution."""
        mock_repository = Mock()
        mock_repository.languages = {"Python": 1000, "JavaScript": 500}

        result = RepositoryNode.languages(mock_repository)
        assert result == ["Python", "JavaScript"]

    def test_latest_release_method(self):
        """Test latest_release method resolution."""
        mock_repository = Mock()
        mock_repository.latest_release = "v1.0.0"

        result = RepositoryNode.latest_release(mock_repository)
        assert result == "v1.0.0"

    def test_organization_method(self):
        """Test organization method resolution."""
        mock_repository = Mock()
        mock_organization = Mock()
        mock_repository.organization = mock_organization

        result = RepositoryNode.organization(mock_repository)
        assert result == mock_organization

    def test_owner_key_method(self):
        """Test owner_key method resolution."""
        mock_repository = Mock()
        mock_repository.owner_key = "test-owner"

        result = RepositoryNode.owner_key(mock_repository)
        assert result == "test-owner"

    def test_project_method(self):
        """Test project method resolution."""
        mock_repository = Mock()
        mock_project = Mock()
        mock_repository.project = mock_project

        result = RepositoryNode.project(mock_repository)
        assert result == mock_project

    def test_recent_milestones_method(self):
        """Test recent_milestones method resolution."""
        mock_repository = Mock()
        mock_milestones = Mock()
        mock_milestones.select_related.return_value.order_by.return_value.__getitem__ = Mock(
            return_value=[]
        )
        mock_repository.recent_milestones = mock_milestones

        RepositoryNode.recent_milestones(mock_repository, limit=3)
        mock_milestones.select_related.assert_called_with("repository")
        mock_milestones.select_related.return_value.order_by.assert_called_with("-created_at")

    def test_releases_method(self):
        """Test releases method resolution."""
        mock_repository = Mock()
        mock_releases = Mock()
        mock_releases.order_by.return_value.__getitem__ = Mock(return_value=[])
        mock_repository.published_releases = mock_releases

        RepositoryNode.releases(mock_repository)
        mock_releases.order_by.assert_called_with("-published_at")

    def test_top_contributors_method(self):
        """Test top_contributors method resolution."""
        mock_repository = Mock()
        mock_contributors = [Mock(), Mock()]
        mock_repository.idx_top_contributors = mock_contributors

        result = RepositoryNode.top_contributors(mock_repository)
        assert result == mock_contributors

    def test_topics_method(self):
        """Test topics method resolution."""
        mock_repository = Mock()
        mock_repository.topics = ["security", "python", "django"]

        result = RepositoryNode.topics(mock_repository)
        assert result == ["security", "python", "django"]

    def test_url_method(self):
        """Test url method resolution."""
        mock_repository = Mock()
        mock_repository.url = "https://github.com/test-org/test-repo"

        result = RepositoryNode.url(mock_repository)
        assert result == "https://github.com/test-org/test-repo"
