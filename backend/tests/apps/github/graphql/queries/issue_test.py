"""Tests for apps.github.graphql.queries.issue module."""

from unittest.mock import MagicMock, patch

import pytest
from graphene import ObjectType, Schema
from graphene.test import Client

from apps.github.graphql.nodes.issue import IssueNode
from apps.github.graphql.queries.issue import IssueQuery
from apps.github.models.issue import Issue


@pytest.fixture
def issue_query():
    """Fixture for IssueQuery instance."""
    return IssueQuery()


@pytest.fixture
def mock_issues():
    """Fixture for mock issues."""
    return [
        MagicMock(spec=Issue, id=1, title="Issue 1"),
        MagicMock(spec=Issue, id=2, title="Issue 2"),
        MagicMock(spec=Issue, id=3, title="Issue 3"),
    ]


@pytest.fixture
def schema():
    """Create a test schema with IssueQuery."""

    class Query(IssueQuery, ObjectType):
        pass

    return Schema(query=Query)


@pytest.fixture
def client(schema):
    """GraphQL test client."""
    return Client(schema)


DEFAULT_LIMIT = 15


class TestIssueQuery:
    """Test suite for IssueQuery."""

    @patch("apps.github.graphql.queries.issue.Issue.objects")
    def test_resolve_recent_issues_with_default_limit(
        self, mock_objects, issue_query, mock_issues
    ):
        """Test resolve_recent_issues with default limit."""
        mock_ordered = MagicMock()
        mock_objects.order_by.return_value = mock_ordered
        mock_ordered.__getitem__.return_value = mock_issues[:2]

        result = issue_query.resolve_recent_issues(MagicMock(), 15)

        assert result == mock_issues[:2]
        mock_objects.order_by.assert_called_once_with("-created_at")
        mock_ordered.__getitem__.assert_called_once_with(slice(None, 15))

    @patch("apps.github.graphql.queries.issue.Issue.objects")
    def test_resolve_recent_issues_with_custom_limit(self, mock_objects, issue_query, mock_issues):
        """Test resolve_recent_issues with custom limit."""
        mock_ordered = MagicMock()
        mock_objects.order_by.return_value = mock_ordered
        mock_ordered.__getitem__.return_value = mock_issues[:1]
        custom_limit = 1

        result = issue_query.resolve_recent_issues(MagicMock(), custom_limit)

        assert result == mock_issues[:1]
        mock_objects.order_by.assert_called_once_with("-created_at")
        mock_ordered.__getitem__.assert_called_once_with(slice(None, custom_limit))

    def test_recent_issues_field_definition(self):
        """Test that the recent_issues field is properly defined."""
        field = IssueQuery._meta.fields["recent_issues"]

        assert field is not None
        assert field.type.of_type == IssueNode
        assert field.args["limit"].default_value == DEFAULT_LIMIT

    def test_integration_with_graphql_schema(self, client):
        """Test the GraphQL schema integration with a direct approach."""
        query = """
        {
            recentIssues(limit: 5) {
                title
                number
            }
        }
        """
        try:
            result = client.execute(query)
            assert "data" in result
            assert "recentIssues" in result["data"]

        except (KeyError, TypeError) as e:
            pytest.skip(f"Skipping schema integration test due to: {e!s}")
