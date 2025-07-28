from unittest.mock import MagicMock

import pytest
from django.contrib.admin.sites import AdminSite

from apps.github.admin.issue import IssueAdmin
from apps.github.models.issue import Issue


@pytest.fixture
def issue_admin_instance():
    return IssueAdmin(model=Issue, admin_site=AdminSite())


class TestIssueAdmin:
    """Test suite for the IssueAdmin class."""

    def test_custom_field_github_url(self, issue_admin_instance):
        """Test that custom_field_github_url generates the correct HTML link."""
        mock_issue = MagicMock()
        mock_issue.url = "https://github.com/mock-org/mock-repo/issues/1"

        result = issue_admin_instance.custom_field_github_url(mock_issue)

        expected_html = (
            "<a href='https://github.com/mock-org/mock-repo/issues/1' target='_blank'>↗️</a>"
        )

        assert result == expected_html

    def test_list_display_contains_custom_field(self, issue_admin_instance):
        """Test that the list_display includes custom fields."""
        assert "custom_field_github_url" in issue_admin_instance.list_display
