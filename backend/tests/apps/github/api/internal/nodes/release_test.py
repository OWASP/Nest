"""Test cases for ReleaseNode."""

from unittest.mock import Mock

from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.user import UserNode


class TestReleaseNode:
    """Test cases for ReleaseNode class."""

    def test_release_node_inheritance(self):
        assert hasattr(ReleaseNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {field.name for field in ReleaseNode.__strawberry_definition__.fields}
        expected_field_names = {
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

    def test_author_resolution(self):
        """Test author field resolution."""
        mock_release = Mock()
        mock_author = Mock()
        mock_release.author = mock_author

        result = ReleaseNode.author(mock_release)
        assert result == mock_author

    def test_organization_name_with_organization(self):
        """Test organization_name field when organization exists."""
        mock_release = Mock()
        mock_repository = Mock()
        mock_organization = Mock()
        mock_organization.login = "test-org"
        mock_repository.organization = mock_organization
        mock_release.repository = mock_repository

        result = ReleaseNode.organization_name(mock_release)
        assert result == "test-org"

    def test_organization_name_without_organization(self):
        """Test organization_name field when organization doesn't exist."""
        mock_release = Mock()
        mock_repository = Mock()
        mock_repository.organization = None
        mock_release.repository = mock_repository

        result = ReleaseNode.organization_name(mock_release)
        assert result is None

    def test_organization_name_without_repository(self):
        """Test organization_name field when repository doesn't exist."""
        mock_release = Mock()
        mock_release.repository = None

        result = ReleaseNode.organization_name(mock_release)
        assert result is None

    def test_project_name_with_project(self):
        """Test project_name field when project exists."""
        mock_release = Mock()
        mock_repository = Mock()
        mock_project = Mock()
        mock_project.name = "OWASP Test Project"
        mock_repository.project = mock_project
        mock_release.repository = mock_repository

        result = ReleaseNode.project_name(mock_release)
        assert result == " Test Project"  # OWASP prefix stripped

    def test_project_name_without_project(self):
        """Test project_name field when project doesn't exist."""
        mock_release = Mock()
        mock_repository = Mock()
        mock_repository.project = None
        mock_release.repository = mock_repository

        result = ReleaseNode.project_name(mock_release)
        assert result is None

    def test_project_name_without_repository(self):
        """Test project_name field when repository doesn't exist."""
        mock_release = Mock()
        mock_release.repository = None

        result = ReleaseNode.project_name(mock_release)
        assert result is None

    def test_repository_name_with_repository(self):
        """Test repository_name field when repository exists."""
        mock_release = Mock()
        mock_repository = Mock()
        mock_repository.name = "test-repo"
        mock_release.repository = mock_repository

        result = ReleaseNode.repository_name(mock_release)
        assert result == "test-repo"

    def test_repository_name_without_repository(self):
        """Test repository_name field when repository doesn't exist."""
        mock_release = Mock()
        mock_release.repository = None

        result = ReleaseNode.repository_name(mock_release)
        assert result is None

    def test_url_field(self):
        """Test url field resolution."""
        mock_release = Mock()
        mock_release.url = "https://github.com/test-org/test-repo/releases/tag/v1.0.0"

        result = ReleaseNode.url(mock_release)
        assert result == "https://github.com/test-org/test-repo/releases/tag/v1.0.0"
