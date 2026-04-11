from unittest.mock import MagicMock

import pytest
from django.contrib.admin.sites import AdminSite

from apps.github.admin.pull_request import PullRequestAdmin
from apps.github.models.pull_request import PullRequest


@pytest.fixture
def pull_request_admin_instance():
    return PullRequestAdmin(model=PullRequest, admin_site=AdminSite())


class TestPullRequestAdmin:
    """Test suite for the PullRequestAdmin class."""

    def test_custom_field_github_url(self, pull_request_admin_instance):
        """Test that custom_field_github_url generates the correct HTML link."""
        mock_pull_request = MagicMock()
        mock_pull_request.url = "https://github.com/mock-org/mock-repo/pull/42"

        result = pull_request_admin_instance.custom_field_github_url(mock_pull_request)

        expected_html = (
            "<a href='https://github.com/mock-org/mock-repo/pull/42' target='_blank'>↗️</a>"
        )

        assert result == expected_html

    def test_list_display_contains_custom_field(self, pull_request_admin_instance):
        """Test that the list_display includes custom fields."""
        assert "custom_field_github_url" in pull_request_admin_instance.list_display
