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

    @patch("apps.github.models.issue.Issue.objects")
    def test_recent_issues_basic(self, mock_objects, mock_issue):
        """Test fetching recent issues with default parameters."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_objects.order_by.return_value = mock_queryset

        result = IssueQuery().recent_issues()

        assert result == [mock_issue]
        mock_objects.order_by.assert_called_once_with("-created_at")

    @patch("apps.github.models.issue.Issue.objects")
    def test_recent_issues_with_login(self, mock_objects, mock_issue):
        """Test filtering issues by login."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_objects.order_by.return_value = mock_queryset

        result = IssueQuery().recent_issues(login="alice")

        mock_queryset.filter.assert_called_once_with(author__login="alice")
        assert result == [mock_issue]

    @patch("apps.github.models.issue.Issue.objects")
    def test_recent_issues_with_organization(self, mock_objects, mock_issue):
        """Test filtering issues by organization."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_objects.order_by.return_value = mock_queryset

        result = IssueQuery().recent_issues(organization="orgX")

        mock_queryset.filter.assert_called_once_with(repository__organization__login="orgX")
        assert result == [mock_issue]

    @patch("apps.github.models.issue.Issue.objects")
    def test_recent_issues_limit(self, mock_objects, mock_issue):
        """Test limiting the number of issues returned."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_objects.order_by.return_value = mock_queryset

        result = IssueQuery().recent_issues(limit=1)

        mock_objects.order_by.assert_called_once_with("-created_at")
        assert result == [mock_issue]

    @patch("apps.github.models.issue.Issue.objects")
    def test_recent_issues_distinct(self, mock_objects, mock_issue):
        """Test distinct filtering with Window/Rank for issues."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_objects.order_by.return_value = mock_queryset

        result = IssueQuery().recent_issues(distinct=True)

        assert result == [mock_issue]
        mock_queryset.annotate.assert_called_once()
        # One filter for empty filters dict, one for rank=1
        assert mock_queryset.filter.call_count == 2
        assert (
            mock_queryset.order_by.call_count == 1
        )  # Only initially, distinct adds order_by directly

    @patch("apps.github.models.issue.Issue.objects")
    def test_recent_issues_combined_filters(self, mock_objects, mock_issue):
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_objects.order_by.return_value = mock_queryset

        result = IssueQuery().recent_issues(login="alice", organization="owasp")

        # Both filters are applied in one call using **filters
        mock_queryset.filter.assert_called_once_with(
            author__login="alice", repository__organization__login="owasp"
        )
        assert result == [mock_issue]

    @patch("apps.github.models.issue.Issue.objects")
    def test_recent_issues_distinct_with_organization(self, mock_objects, mock_issue):
        """Test distinct filtering with organization filter."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_objects.order_by.return_value = mock_queryset

        result = IssueQuery().recent_issues(distinct=True, organization="owasp")

        assert result == [mock_issue]
        mock_queryset.annotate.assert_called_once()
        # One filter for organization, one for rank=1
        assert mock_queryset.filter.call_count == 2

    @patch("apps.github.models.issue.Issue.objects")
    def test_recent_issues_distinct_with_all_filters(self, mock_objects, mock_issue):
        """Test distinct filtering with all filters."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.annotate.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_objects.order_by.return_value = mock_queryset

        result = IssueQuery().recent_issues(
            distinct=True, login="alice", organization="owasp", limit=3
        )

        assert result == [mock_issue]
        mock_queryset.annotate.assert_called_once()
        # One filter for login+organization combined, one for rank=1
        assert mock_queryset.filter.call_count == 2
        mock_queryset.__getitem__.assert_called_with(slice(None, 3))

    @patch("apps.github.models.issue.Issue.objects")
    def test_recent_issues_organization_only(self, mock_objects, mock_issue):
        """Test filtering issues by organization only."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_objects.order_by.return_value = mock_queryset

        result = IssueQuery().recent_issues(organization="owasp")

        assert result == [mock_issue]
        mock_queryset.filter.assert_called_once_with(repository__organization__login="owasp")

    @patch("apps.github.models.issue.Issue.objects")
    def test_recent_issues_multiple_filters(self, mock_objects, mock_issue):
        """Test issues with multiple filters applied."""
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_issue]
        mock_objects.order_by.return_value = mock_queryset

        result = IssueQuery().recent_issues(organization="owasp", limit=10)

        assert result == [mock_issue]
        # Verify organization filter was applied
        mock_queryset.filter.assert_called_once_with(repository__organization__login="owasp")
        mock_queryset.__getitem__.assert_called_with(slice(None, 10))
