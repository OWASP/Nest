"""Test cases for IssueNode."""

from unittest.mock import Mock

from apps.github.api.internal.nodes.issue import IssueNode


class TestIssueNode:
    """Test cases for IssueNode class."""

    def test_issue_node_type(self):
        assert hasattr(IssueNode, "__strawberry_definition__")

    def test_issue_node_fields(self):
        field_names = {field.name for field in IssueNode.__strawberry_definition__.fields}
        expected_field_names = {
            "created_at",
            "state",
            "title",
            "url",
            "author",
            "organization_name",
            "repository_name",
        }
        assert field_names == expected_field_names

    def test_author_field(self):
        """Test author field resolution."""
        mock_issue = Mock()
        mock_author = Mock()
        mock_issue.author = mock_author

        result = IssueNode.author(mock_issue)
        assert result == mock_author

    def test_organization_name_with_organization(self):
        """Test organization_name field when organization exists."""
        mock_issue = Mock()
        mock_repository = Mock()
        mock_organization = Mock()
        mock_organization.login = "test-org"
        mock_repository.organization = mock_organization
        mock_issue.repository = mock_repository

        result = IssueNode.organization_name(mock_issue)
        assert result == "test-org"

    def test_organization_name_without_organization(self):
        """Test organization_name field when organization doesn't exist."""
        mock_issue = Mock()
        mock_repository = Mock()
        mock_repository.organization = None
        mock_issue.repository = mock_repository

        result = IssueNode.organization_name(mock_issue)
        assert result is None

    def test_organization_name_without_repository(self):
        """Test organization_name field when repository doesn't exist."""
        mock_issue = Mock()
        mock_issue.repository = None

        result = IssueNode.organization_name(mock_issue)
        assert result is None

    def test_repository_name_with_repository(self):
        """Test repository_name field when repository exists."""
        mock_issue = Mock()
        mock_repository = Mock()
        mock_repository.name = "test-repo"
        mock_issue.repository = mock_repository

        result = IssueNode.repository_name(mock_issue)
        assert result == "test-repo"

    def test_repository_name_without_repository(self):
        """Test repository_name field when repository doesn't exist."""
        mock_issue = Mock()
        mock_issue.repository = None

        result = IssueNode.repository_name(mock_issue)
        assert result is None
