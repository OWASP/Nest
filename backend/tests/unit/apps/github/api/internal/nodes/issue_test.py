"""Test cases for IssueNode."""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

from apps.github.api.internal.nodes.issue import IssueNode
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


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

    def test_labels(self):
        """Test labels field returns list of label names."""
        mock_issue = Mock()
        mock_label1 = Mock()
        mock_label1.name = "bug"
        mock_label2 = Mock()
        mock_label2.name = "enhancement"
        mock_issue.labels.all.return_value = [mock_label1, mock_label2]

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

    def test_task_deadline_with_bulk_load_mapping(self):
        """Test task_deadline field when mapping exists with issue deadline."""
        expected_date = datetime(2025, 10, 26, tzinfo=UTC)
        mock_issue = Mock()
        mock_issue.number = 123

        mock_info = Mock()
        mock_info.context = Mock()
        mock_info.context.task_deadlines_by_issue = {123: expected_date}

        field = self._get_field_by_name("task_deadline", IssueNode)
        result = field.base_resolver.wrapped_func(None, mock_issue, mock_info)
        assert result == expected_date

    def test_task_deadline_with_bulk_load_mapping_no_deadline(self):
        """Test task_deadline field when mapping exists but issue not in mapping."""
        mock_issue = Mock()
        mock_issue.number = 123

        mock_info = Mock()
        mock_info.context = Mock()
        mock_info.context.task_deadlines_by_issue = {456: datetime(2025, 10, 26, tzinfo=UTC)}

        field = self._get_field_by_name("task_deadline", IssueNode)
        result = field.base_resolver.wrapped_func(None, mock_issue, mock_info)
        assert result is None

    def test_task_deadline_without_bulk_load_mapping(self):
        """Test task_deadline field when no mapping exists (fallback to query)."""
        expected_date = datetime(2025, 10, 26, tzinfo=UTC)
        mock_issue = Mock()
        mock_issue.number = 123

        mock_info = Mock()
        mock_info.context = Mock()
        mock_info.context.task_deadlines_by_issue = None

        with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects:
            mock_query = mock_task_objects.filter.return_value.order_by.return_value
            mock_query.values_list.return_value.first.return_value = expected_date

            field = self._get_field_by_name("task_deadline", IssueNode)
            result = field.base_resolver.wrapped_func(None, mock_issue, mock_info)
            assert result == expected_date
            mock_task_objects.filter.assert_called_once_with(
                issue=mock_issue, deadline_at__isnull=False
            )
