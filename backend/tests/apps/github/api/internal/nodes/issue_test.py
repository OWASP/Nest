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

    def test_labels(self):
        """Test labels field returns list of label names."""
        mock_issue = Mock()
        mock_label1 = Mock()
        mock_label1.name = "bug"
        mock_label2 = Mock()
        mock_label2.name = "enhancement"
        mock_issue.label_names = [mock_label1, mock_label2]

        field = self._get_field_by_name("labels", IssueNode)
        result = field.base_resolver.wrapped_func(None, mock_issue)
        assert result == ["bug", "enhancement"]

    def test_is_merged_true(self):
        """Test is_merged field when issue has merged pull requests."""
        mock_issue = Mock()
        mock_issue.merged_pull_requests = [Mock()]

        field = self._get_field_by_name("is_merged", IssueNode)
        result = field.base_resolver.wrapped_func(None, mock_issue)
        assert result

    def test_is_merged_false(self):
        """Test is_merged field when issue has no merged pull requests."""
        mock_issue = Mock()
        mock_issue.merged_pull_requests = None

        field = self._get_field_by_name("is_merged", IssueNode)
        result = field.base_resolver.wrapped_func(None, mock_issue)
        assert not result

    def test_interested_users(self):
        """Test interested_users field returns list of users from prefetched interests_users."""
        mock_issue = Mock()
        mock_user1 = Mock()
        mock_user1.login = "user1"
        mock_user2 = Mock()
        mock_user2.login = "user2"

        mock_interest1 = Mock()
        mock_interest1.user = mock_user1
        mock_interest2 = Mock()
        mock_interest2.user = mock_user2

        mock_issue.interests_users = [mock_interest1, mock_interest2]

        field = self._get_field_by_name("interested_users", IssueNode)
        result = field.base_resolver.wrapped_func(None, mock_issue)
        assert result == [mock_user1, mock_user2]
