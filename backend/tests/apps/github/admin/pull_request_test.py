"""Tests for GitHub app PullRequestAdmin."""

from unittest.mock import MagicMock

from django.contrib.admin.sites import AdminSite

from apps.github.admin.pull_request import PullRequestAdmin
from apps.github.models.pull_request import PullRequest


class TestPullRequestAdmin:
    """Test cases for PullRequestAdmin."""

    def setup_method(self):
        """Set up test fixtures."""
        self.site = AdminSite()
        self.admin = PullRequestAdmin(PullRequest, self.site)

    # --- configuration ---

    def test_list_display_contains_expected_fields(self):
        """Test list_display contains all required column fields."""
        assert "repository" in self.admin.list_display
        assert "title" in self.admin.list_display
        assert "state" in self.admin.list_display
        assert "custom_field_github_url" in self.admin.list_display
        assert "created_at" in self.admin.list_display
        assert "updated_at" in self.admin.list_display

    def test_list_filter_contains_state_and_merged_at(self):
        """Test list_filter contains state and merged_at filters."""
        assert "state" in self.admin.list_filter
        assert "merged_at" in self.admin.list_filter

    def test_search_fields_contains_relevant_fields(self):
        """Test search_fields allows searching by title, author, and repo."""
        assert "title" in self.admin.search_fields
        assert "author__login" in self.admin.search_fields
        assert "repository__name" in self.admin.search_fields

    def test_autocomplete_fields(self):
        """Test autocomplete_fields includes all many-to-many FK fields."""
        assert "assignees" in self.admin.autocomplete_fields
        assert "author" in self.admin.autocomplete_fields
        assert "labels" in self.admin.autocomplete_fields
        assert "related_issues" in self.admin.autocomplete_fields
        assert "repository" in self.admin.autocomplete_fields

    # --- custom_field_github_url ---

    def test_custom_field_github_url_returns_anchor_tag(self):
        """Test custom_field_github_url returns an anchor tag with the PR URL."""
        obj = MagicMock()
        obj.url = "https://github.com/OWASP/Nest/pull/42"

        result = self.admin.custom_field_github_url(obj)

        assert "href" in result
        assert "https://github.com/OWASP/Nest/pull/42" in result
        assert 'target="_blank"' in result
        assert "↗️" in result

    def test_custom_field_github_url_exact_html(self):
        """Test custom_field_github_url produces the expected exact HTML."""
        obj = MagicMock()
        obj.url = "https://github.com/mock-org/mock-repo/pull/42"

        result = self.admin.custom_field_github_url(obj)
        expected = (
            "<a href='https://github.com/mock-org/mock-repo/pull/42' target='_blank'>↗️</a>"
        )

        assert result == expected

    def test_custom_field_github_url_short_description(self):
        """Test custom_field_github_url has correct short_description label."""
        assert self.admin.custom_field_github_url.short_description == "GitHub 🔗"

    def test_custom_field_github_url_with_high_pr_number(self):
        """Test custom_field_github_url works with large PR numbers."""
        obj = MagicMock()
        obj.url = "https://github.com/django/django/pull/99999"

        result = self.admin.custom_field_github_url(obj)

        assert "https://github.com/django/django/pull/99999" in result
