"""Test cases for PullRequestNode."""

from unittest.mock import Mock

from apps.github.api.internal.nodes.pull_request import PullRequestNode


class TestPullRequestNode:
    """Test cases for PullRequestNode class."""

    def test_pull_request_node_type(self):
        assert hasattr(PullRequestNode, "__strawberry_definition__")

    def test_pull_request_node_fields(self):
        field_names = {field.name for field in PullRequestNode.__strawberry_definition__.fields}
        expected_field_names = {
            "author",
            "created_at",
            "organization_name",
            "repository_name",
            "title",
            "url",
        }
        assert field_names == expected_field_names

    def test_author_field(self):
        """Test author field resolution."""
        mock_pr = Mock()
        mock_author = Mock()
        mock_pr.author = mock_author

        result = PullRequestNode.author(mock_pr)
        assert result == mock_author

    def test_organization_name_with_organization(self):
        """Test organization_name field when organization exists."""
        mock_pr = Mock()
        mock_repository = Mock()
        mock_organization = Mock()
        mock_organization.login = "test-org"
        mock_repository.organization = mock_organization
        mock_pr.repository = mock_repository

        result = PullRequestNode.organization_name(mock_pr)
        assert result == "test-org"

    def test_organization_name_without_organization(self):
        """Test organization_name field when organization doesn't exist."""
        mock_pr = Mock()
        mock_repository = Mock()
        mock_repository.organization = None
        mock_pr.repository = mock_repository

        result = PullRequestNode.organization_name(mock_pr)
        assert result is None

    def test_organization_name_without_repository(self):
        """Test organization_name field when repository doesn't exist."""
        mock_pr = Mock()
        mock_pr.repository = None

        result = PullRequestNode.organization_name(mock_pr)
        assert result is None

    def test_repository_name_with_repository(self):
        """Test repository_name field when repository exists."""
        mock_pr = Mock()
        mock_repository = Mock()
        mock_repository.name = "test-repo"
        mock_pr.repository = mock_repository

        result = PullRequestNode.repository_name(mock_pr)
        assert result == "test-repo"

    def test_repository_name_without_repository(self):
        """Test repository_name field when repository doesn't exist."""
        mock_pr = Mock()
        mock_pr.repository = None

        result = PullRequestNode.repository_name(mock_pr)
        assert result is None

    def test_url_with_url(self):
        """Test url field when URL exists."""
        mock_pr = Mock()
        mock_pr.url = "https://github.com/test-org/test-repo/pull/123"

        result = PullRequestNode.url(mock_pr)
        assert result == "https://github.com/test-org/test-repo/pull/123"

    def test_url_without_url(self):
        """Test url field when URL doesn't exist."""
        mock_pr = Mock()
        mock_pr.url = None

        result = PullRequestNode.url(mock_pr)
        assert result == ""
