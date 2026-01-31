"""Test cases for IssueNode."""

from unittest.mock import Mock

from apps.github.api.internal.nodes.issue import IssueNode
from tests.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestIssueNode(GraphQLNodeBaseTest):
    """Test cases for IssueNode class."""

    def test_issue_node_type(self):
        assert hasattr(IssueNode, "__strawberry_definition__")

    def test_issue_node_fields(self):
        field_names = {field.name for field in IssueNode.__strawberry_definition__.fields}
        expected_field_names = {
            "_id",
            "assignees",
            "author",
            "body",
            "created_at",
            "interested_users",
            "is_merged",
            "labels",
            "number",
            "organization_name",
            "pull_requests",
            "repository_name",
            "state",
            "task_deadline",
            "title",
            "url",
        }
        assert field_names == expected_field_names

    def test_organization_name_with_organization(self):
        """Test organization_name field when organization exists."""
        mock_issue = Mock()
        mock_repository = Mock()
        mock_organization = Mock()
        mock_organization.login = "test-org"
        mock_repository.organization = mock_organization
        mock_issue.repository = mock_repository

        field = self._get_field_by_name("organization_name", IssueNode)
        result = field.base_resolver.wrapped_func(None, mock_issue)
        assert result == "test-org"

    def test_organization_name_without_organization(self):
        """Test organization_name field when organization doesn't exist."""
        mock_issue = Mock()
        mock_repository = Mock()
        mock_repository.organization = None
        mock_issue.repository = mock_repository

        field = self._get_field_by_name("organization_name", IssueNode)
        result = field.base_resolver.wrapped_func(None, mock_issue)
        assert result is None

    def test_organization_name_without_repository(self):
        """Test organization_name field when repository doesn't exist."""
        mock_issue = Mock()
        mock_issue.repository = None

        field = self._get_field_by_name("organization_name", IssueNode)
        result = field.base_resolver.wrapped_func(None, mock_issue)
        assert result is None

    def test_repository_name_with_repository(self):
        """Test repository_name field when repository exists."""
        mock_issue = Mock()
        mock_repository = Mock()
        mock_repository.name = "test-repo"
        mock_issue.repository = mock_repository

        field = self._get_field_by_name("repository_name", IssueNode)
        result = field.base_resolver.wrapped_func(None, mock_issue)
        assert result == "test-repo"

    def test_repository_name_without_repository(self):
        """Test repository_name field when repository doesn't exist."""
        mock_issue = Mock()
        mock_issue.repository = None

        field = self._get_field_by_name("repository_name", IssueNode)
        result = field.base_resolver.wrapped_func(None, mock_issue)
        assert result is None
