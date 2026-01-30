from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from ninja.responses import Response

from apps.api.rest.v0.issue import (
    IssueDetail,
    IssueFilter,
    get_issue,
    list_issues,
)
from apps.github.models.issue import Issue as IssueModel


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
    """Tests for list_issues view function."""

    def test_list_issues_no_filter(self, mocker):
        """Test listing issues without filters."""
        mock_qs = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.order_by.return_value = []
        mocker.patch(
            "apps.api.rest.v0.issue.IssueModel.objects",
            mock_qs,
        )

        request = MagicMock()
        filters = IssueFilter()
        list_issues(request, filters, None)

        mock_qs.order_by.assert_called_once_with("-created_at", "-updated_at")

    def test_list_issues_with_organization_filter(self, mocker):
        """Test listing issues with organization filter."""
        mock_qs = MagicMock()
        mock_filtered = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.filter.return_value = mock_filtered
        mock_filtered.order_by.return_value = []
        mocker.patch(
            "apps.api.rest.v0.issue.IssueModel.objects",
            mock_qs,
        )

        request = MagicMock()
        filters = IssueFilter(organization="OWASP")
        list_issues(request, filters, None)

        mock_qs.filter.assert_called_with(repository__organization__login__iexact="OWASP")

    def test_list_issues_with_repository_filter(self, mocker):
        """Test listing issues with repository filter."""
        mock_qs = MagicMock()
        mock_filtered = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.filter.return_value = mock_filtered
        mock_filtered.filter.return_value = mock_filtered
        mock_filtered.order_by.return_value = []
        mocker.patch(
            "apps.api.rest.v0.issue.IssueModel.objects",
            mock_qs,
        )

        request = MagicMock()
        filters = IssueFilter(organization="OWASP", repository="Nest")
        list_issues(request, filters, None)

        mock_filtered.filter.assert_called_with(repository__name__iexact="Nest")

    def test_list_issues_with_state_filter(self, mocker):
        """Test listing issues with state filter."""
        mock_qs = MagicMock()
        mock_filtered = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.filter.return_value = mock_filtered
        mock_filtered.filter.return_value = mock_filtered
        mock_filtered.order_by.return_value = []
        mocker.patch(
            "apps.api.rest.v0.issue.IssueModel.objects",
            mock_qs,
        )

        request = MagicMock()
        filters = IssueFilter(state="open")
        list_issues(request, filters, None)

    def test_list_issues_with_ordering(self, mocker):
        """Test listing issues with custom ordering."""
        mock_qs = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.order_by.return_value = []
        mocker.patch(
            "apps.api.rest.v0.issue.IssueModel.objects",
            mock_qs,
        )

        request = MagicMock()
        filters = IssueFilter()
        list_issues(request, filters, "updated_at")

        mock_qs.order_by.assert_called_once_with("updated_at", "-updated_at")


class TestGetIssue:
    """Tests for get_issue view function."""

    def test_get_issue_success(self, mocker):
        """Test getting a specific issue successfully."""
        mock_issue = MagicMock()
        mock_qs = MagicMock()
        mock_qs.get.return_value = mock_issue
        mocker.patch(
            "apps.api.rest.v0.issue.IssueModel.objects",
            mock_qs,
        )

        request = MagicMock()
        result = get_issue(request, "OWASP", "Nest", 123)

        assert result == mock_issue
        mock_qs.get.assert_called_once_with(
            repository__organization__login__iexact="OWASP",
            repository__name__iexact="Nest",
            number=123,
        )

    def test_get_issue_not_found(self, mocker):
        """Test getting a non-existent issue."""
        mock_qs = MagicMock()
        mock_qs.get.side_effect = IssueModel.DoesNotExist
        mocker.patch(
            "apps.api.rest.v0.issue.IssueModel.objects",
            mock_qs,
        )

        request = MagicMock()
        result = get_issue(request, "OWASP", "NonExistent", 999)

        assert isinstance(result, Response)
        assert result.status_code == HTTPStatus.NOT_FOUND
