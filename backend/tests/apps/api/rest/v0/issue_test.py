from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.issue import IssueDetail, get_issue, list_issues


class TestIssueSchema:
    @pytest.mark.parametrize(
        "issue_data",
        [
            {
                "body": "This is a test issue 1",
                "created_at": "2024-12-30T00:00:00Z",
                "state": "open",
                "title": "Test Issue 1",
                "updated_at": "2024-12-30T00:00:00Z",
                "url": "https://example.com/issues/1",
            },
            {
                "body": "This is a test issue 2",
                "created_at": "2024-12-29T00:00:00Z",
                "state": "closed",
                "title": "Test Issue 2",
                "updated_at": "2024-12-30T00:00:00Z",
                "url": "https://example.com/issues/2",
            },
        ],
    )
    def test_issue_schema(self, issue_data):
        issue = IssueDetail(**issue_data)

        assert issue.body == issue_data["body"]
        assert issue.created_at == datetime.fromisoformat(issue_data["created_at"])
        assert issue.state == issue_data["state"]
        assert issue.title == issue_data["title"]
        assert issue.updated_at == datetime.fromisoformat(issue_data["updated_at"])
        assert issue.url == issue_data["url"]


class TestListIssues:
    """Test cases for list_issues endpoint."""

    @patch("apps.api.rest.v0.issue.IssueModel.objects")
    def test_list_issues_with_organization_filter(self, mock_objects):
        """Test listing issues filtered by organization."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = "OWASP"
        mock_filters.repository = None
        mock_filters.state = None

        mock_select_related = MagicMock()
        mock_filtered = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select_related
        mock_select_related.filter.return_value = mock_filtered
        mock_filtered.order_by.return_value = mock_ordered

        result = list_issues(mock_request, filters=mock_filters, ordering=None)

        mock_objects.select_related.assert_called_once_with(
            "repository", "repository__organization"
        )
        mock_select_related.filter.assert_called_once_with(
            repository__organization__login__iexact="OWASP"
        )
        mock_filtered.order_by.assert_called_once_with("-created_at", "-updated_at", "id")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.issue.IssueModel.objects")
    def test_list_issues_with_repository_filter(self, mock_objects):
        """Test listing issues filtered by repository."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = None
        mock_filters.repository = "Nest"
        mock_filters.state = None

        mock_select_related = MagicMock()
        mock_filtered = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select_related
        mock_select_related.filter.return_value = mock_filtered
        mock_filtered.order_by.return_value = mock_ordered

        result = list_issues(mock_request, filters=mock_filters, ordering=None)

        mock_objects.select_related.assert_called_once_with(
            "repository", "repository__organization"
        )
        mock_select_related.filter.assert_called_once_with(repository__name__iexact="Nest")
        mock_filtered.order_by.assert_called_once_with("-created_at", "-updated_at", "id")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.issue.IssueModel.objects")
    def test_list_issues_with_state_filter(self, mock_objects):
        """Test listing issues filtered by state."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = None
        mock_filters.repository = None
        mock_filters.state = "open"

        mock_select_related = MagicMock()
        mock_filtered = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select_related
        mock_select_related.filter.return_value = mock_filtered
        mock_filtered.order_by.return_value = mock_ordered

        result = list_issues(mock_request, filters=mock_filters, ordering=None)

        mock_objects.select_related.assert_called_once_with(
            "repository", "repository__organization"
        )
        mock_select_related.filter.assert_called_once_with(state="open")
        mock_filtered.order_by.assert_called_once_with("-created_at", "-updated_at", "id")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.issue.IssueModel.objects")
    def test_list_issues_with_custom_ordering(self, mock_objects):
        """Test listing issues with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = None
        mock_filters.repository = None
        mock_filters.state = None

        mock_select_related = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select_related
        mock_select_related.order_by.return_value = mock_ordered

        result = list_issues(mock_request, filters=mock_filters, ordering="created_at")

        mock_objects.select_related.assert_called_once_with(
            "repository", "repository__organization"
        )
        mock_select_related.order_by.assert_called_once_with("created_at", "id")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.issue.IssueModel.objects")
    def test_list_issues_ordering_by_updated_at(self, mock_objects):
        """Test listing issues with ordering by updated_at avoids double ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = None
        mock_filters.repository = None
        mock_filters.state = None

        mock_select_related = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select_related
        mock_select_related.order_by.return_value = mock_ordered

        result = list_issues(mock_request, filters=mock_filters, ordering="-updated_at")

        mock_objects.select_related.assert_called_once_with(
            "repository", "repository__organization"
        )
        mock_select_related.order_by.assert_called_once_with("-updated_at", "id")
        assert result == mock_ordered


class TestGetIssue:
    """Test cases for get_issue endpoint."""

    @patch("apps.api.rest.v0.issue.IssueModel.objects")
    def test_get_issue_found(self, mock_objects):
        """Test getting an issue that exists."""
        mock_request = MagicMock()
        mock_issue = MagicMock()

        mock_objects.get.return_value = mock_issue

        result = get_issue(
            mock_request, organization_id="OWASP", repository_id="Nest", issue_id=1234
        )

        mock_objects.get.assert_called_once_with(
            repository__organization__login__iexact="OWASP",
            repository__name__iexact="Nest",
            number=1234,
        )
        assert result == mock_issue

    @patch("apps.api.rest.v0.issue.IssueModel.objects")
    def test_get_issue_not_found(self, mock_objects):
        """Test getting an issue that does not exist returns 404."""
        from apps.github.models.issue import Issue as IssueModel

        mock_request = MagicMock()

        mock_objects.get.side_effect = IssueModel.DoesNotExist

        result = get_issue(
            mock_request, organization_id="OWASP", repository_id="Nest", issue_id=9999
        )

        mock_objects.get.assert_called_once_with(
            repository__organization__login__iexact="OWASP",
            repository__name__iexact="Nest",
            number=9999,
        )
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert b"Issue not found" in result.content
