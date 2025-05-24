"""Test cases for IssueQuery."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from apps.github.graphql.queries.issue import IssueQuery
from apps.github.models.issue import Issue


class TestIssueQuery:
    """Test cases for IssueQuery class."""

    @pytest.fixture
    def mock_issue(self):
        """Mock Issue instance."""
        issue = Mock(spec=Issue)
        issue.id = 1
        issue.author_id = 42
        return issue

    @patch("apps.github.models.issue.Issue.objects.select_related")
    def test_recent_issues_basic(self, mock_select_related, mock_issue):
        """Test fetching recent issues with default parameters."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = [mock_issue]
        mock_select_related.return_value = mock_queryset

        result = IssueQuery().recent_issues()

        assert result == [mock_issue]
        mock_select_related.assert_called_once_with(
            "author", "repository", "repository__organization"
        )
        mock_queryset.order_by.assert_called_once_with("-created_at")

    @patch("apps.github.models.issue.Issue.objects.select_related")
    def test_recent_issues_with_login(self, mock_select_related, mock_issue):
        """Test filtering issues by login."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value.filter.return_value = [mock_issue]
        mock_select_related.return_value = mock_queryset

        result = IssueQuery().recent_issues(login="alice")

        mock_select_related.assert_called_once()
        mock_queryset.order_by.assert_called_once()
        mock_queryset.order_by.return_value.filter.assert_called_once_with(author__login="alice")
        assert result == [mock_issue]

    @patch("apps.github.models.issue.Issue.objects.select_related")
    def test_recent_issues_with_organization(self, mock_select_related, mock_issue):
        """Test filtering issues by organization."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value.filter.return_value = [mock_issue]
        mock_select_related.return_value = mock_queryset

        result = IssueQuery().recent_issues(organization="orgX")

        mock_queryset.order_by.assert_called_once()
        mock_queryset.order_by.return_value.filter.assert_called_once_with(
            repository__organization__login="orgX"
        )
        assert result == [mock_issue]

    @patch("apps.github.models.issue.Issue.objects.select_related")
    def test_recent_issues_limit(self, mock_select_related, mock_issue):
        """Test limiting the number of issues returned."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value.__getitem__.return_value = [mock_issue]
        mock_select_related.return_value = mock_queryset

        result = IssueQuery().recent_issues(limit=1)

        mock_select_related.assert_called_once()
        mock_queryset.order_by.assert_called_once_with("-created_at")
        assert result == [mock_issue]
