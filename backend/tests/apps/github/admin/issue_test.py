"""Tests for GitHub app IssueAdmin."""

from unittest.mock import MagicMock

from django.contrib.admin.sites import AdminSite

from apps.github.admin.issue import IssueAdmin
from apps.github.models.issue import Issue


class TestIssueAdmin:
    """Test cases for IssueAdmin."""

    def setup_method(self):
        """Set up test fixtures."""
        self.site = AdminSite()
        self.admin = IssueAdmin(Issue, self.site)

    # --- configuration ---

    def test_list_display_contains_expected_fields(self):
        """Test list_display contains all required column fields."""
        assert "repository" in self.admin.list_display
        assert "title" in self.admin.list_display
        assert "level" in self.admin.list_display
        assert "created_at" in self.admin.list_display
        assert "custom_field_github_url" in self.admin.list_display

    def test_list_filter_contains_state_and_locked(self):
        """Test list_filter contains state and is_locked filters."""
        assert "state" in self.admin.list_filter
        assert "is_locked" in self.admin.list_filter

    def test_search_fields_contains_title(self):
        """Test search_fields allows searching by issue title."""
        assert "title" in self.admin.search_fields

    def test_autocomplete_fields(self):
        """Test autocomplete_fields contains expected FK fields."""
        assert "repository" in self.admin.autocomplete_fields
        assert "author" in self.admin.autocomplete_fields
        assert "assignees" in self.admin.autocomplete_fields
        assert "labels" in self.admin.autocomplete_fields

    # --- custom_field_github_url ---

    def test_custom_field_github_url_returns_anchor_tag(self):
        """Test custom_field_github_url returns an anchor tag with the issue URL."""
        obj = MagicMock()
        obj.url = "https://github.com/OWASP/Nest/issues/42"

        result = self.admin.custom_field_github_url(obj)

        assert "href" in result
        assert "https://github.com/OWASP/Nest/issues/42" in result
        assert 'target="_blank"' in result
        assert "↗️" in result

    def test_custom_field_github_url_exact_html(self):
        """Test custom_field_github_url produces the expected exact HTML."""
        obj = MagicMock()
        obj.url = "https://github.com/mock-org/mock-repo/issues/1"

        result = self.admin.custom_field_github_url(obj)
        expected = (
            "<a href='https://github.com/mock-org/mock-repo/issues/1' target='_blank'>↗️</a>"
        )

        assert result == expected

    def test_custom_field_github_url_short_description(self):
        """Test custom_field_github_url has correct short_description label."""
        assert self.admin.custom_field_github_url.short_description == "GitHub 🔗"

    def test_custom_field_github_url_different_issue(self):
        """Test custom_field_github_url works with any issue URL."""
        obj = MagicMock()
        obj.url = "https://github.com/django/django/issues/999"

        result = self.admin.custom_field_github_url(obj)

        assert "https://github.com/django/django/issues/999" in result
