"""Test cases for IssueQuery."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from apps.github.api.internal.queries.issue import IssueQuery
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

    @patch("apps.github.api.internal.queries.issue.Subquery")
    @patch("apps.github.models.issue.Issue.objects.select_related")
    def test_recent_issues_distinct(self, mock_select_related, mock_subquery, mock_issue):
        """Test distinct filtering with Subquery for issues."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_select_related.return_value = mock_queryset

        mock_subquery_instance = MagicMock()
        mock_subquery.return_value = mock_subquery_instance

        result = IssueQuery().recent_issues(distinct=True)

        assert result == [mock_issue]
        mock_subquery.assert_called_once()
        mock_queryset.filter.assert_called()

    @patch("apps.github.models.issue.Issue.objects.select_related")
    def test_recent_issues_combined_filters(self, mock_select_related, mock_issue):
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value.filter.return_value.filter.return_value = [mock_issue]
        mock_select_related.return_value = mock_queryset

        result = IssueQuery().recent_issues(login="alice", organization="owasp")

        mock_select_related.assert_called_once()
        mock_queryset.order_by.assert_called_once()
        assert result == [mock_issue]

    @patch("apps.github.api.internal.queries.issue.OuterRef")
    @patch("apps.github.api.internal.queries.issue.Subquery")
    @patch("apps.github.models.issue.Issue.objects.select_related")
    def test_recent_issues_distinct_with_organization(
        self, mock_select_related, mock_subquery, mock_outer_ref, mock_issue
    ):
        """Test distinct filtering with organization filter."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_select_related.return_value = mock_queryset

        mock_subquery_instance = Mock()
        mock_subquery.return_value = mock_subquery_instance
        mock_outer_ref_instance = Mock()
        mock_outer_ref.return_value = mock_outer_ref_instance

        result = IssueQuery().recent_issues(distinct=True, organization="owasp")

        assert result == [mock_issue]
        mock_subquery.assert_called_once()
        mock_outer_ref.assert_called_once_with("author_id")

    @patch("apps.github.api.internal.queries.issue.OuterRef")
    @patch("apps.github.api.internal.queries.issue.Subquery")
    @patch("apps.github.models.issue.Issue.objects.select_related")
    def test_recent_issues_distinct_with_all_filters(
        self, mock_select_related, mock_subquery, mock_outer_ref, mock_issue
    ):
        """Test distinct filtering with all filters."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_select_related.return_value = mock_queryset

        mock_subquery_instance = Mock()
        mock_subquery.return_value = mock_subquery_instance
        mock_outer_ref_instance = Mock()
        mock_outer_ref.return_value = mock_outer_ref_instance

        result = IssueQuery().recent_issues(
            distinct=True, login="alice", organization="owasp", limit=3
        )

        assert result == [mock_issue]
        mock_subquery.assert_called_once()
        mock_outer_ref.assert_called_once_with("author_id")
        # Verify both login and organization filters were applied
        assert mock_queryset.filter.call_count >= 3  # login, organization, distinct

    @patch("apps.github.models.issue.Issue.objects.select_related")
    def test_recent_issues_organization_only(self, mock_select_related, mock_issue):
        """Test filtering issues by organization only."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_select_related.return_value = mock_queryset

        result = IssueQuery().recent_issues(organization="owasp")

        assert result == [mock_issue]
        assert len(mock_queryset.filter.call_args_list) >= 1

    @patch("apps.github.models.issue.Issue.objects.select_related")
    def test_recent_issues_multiple_filters(self, mock_select_related, mock_issue):
        """Test issues with multiple filters applied."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_select_related.return_value = mock_queryset

        result = IssueQuery().recent_issues(organization="owasp", limit=10)

        assert result == [mock_issue]
        # Verify organization filter was applied
        assert len(mock_queryset.filter.call_args_list) >= 1
        mock_queryset.__getitem__.assert_called_with(slice(None, 10))
