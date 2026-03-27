"""Tests for GitHub app RepositoryAdmin."""

from unittest.mock import MagicMock

from django.contrib.admin.sites import AdminSite

from apps.github.admin.repository import RepositoryAdmin
from apps.github.models.repository import Repository


class TestRepositoryAdmin:
    """Test cases for RepositoryAdmin."""

    def setup_method(self):
        """Set up test fixtures."""
        self.site = AdminSite()
        self.admin = RepositoryAdmin(Repository, self.site)

    # --- configuration ---

    def test_list_display_contains_expected_fields(self):
        """Test list_display contains all required column fields."""
        assert "custom_field_title" in self.admin.list_display
        assert "custom_field_github_url" in self.admin.list_display
        assert "stars_count" in self.admin.list_display
        assert "forks_count" in self.admin.list_display
        assert "commits_count" in self.admin.list_display
        assert "created_at" in self.admin.list_display
        assert "updated_at" in self.admin.list_display

    def test_ordering_is_descending_created_at(self):
        """Test ordering is by descending created_at."""
        assert self.admin.ordering == ("-created_at",)

    def test_search_fields_contains_name_and_node_id(self):
        """Test search_fields allows querying by name and node_id."""
        assert "name" in self.admin.search_fields
        assert "node_id" in self.admin.search_fields

    def test_list_filter_contains_expected_filters(self):
        """Test list_filter includes archival, fork, template, and org filters."""
        assert "is_archived" in self.admin.list_filter
        assert "is_fork" in self.admin.list_filter
        assert "is_template" in self.admin.list_filter
        assert "is_owasp_repository" in self.admin.list_filter
        assert "organization" in self.admin.list_filter

    def test_autocomplete_fields(self):
        """Test autocomplete_fields contains owner and organization."""
        assert "organization" in self.admin.autocomplete_fields
        assert "owner" in self.admin.autocomplete_fields

    # --- custom_field_title ---

    def test_custom_field_title_returns_owner_slash_name(self):
        """Test custom_field_title formats the title as 'owner/name'."""
        obj = MagicMock()
        obj.owner.login = "OWASP"
        obj.name = "Nest"

        assert self.admin.custom_field_title(obj) == "OWASP/Nest"

    def test_custom_field_title_with_different_owner(self):
        """Test custom_field_title works with any owner/name combination."""
        obj = MagicMock()
        obj.owner.login = "torvalds"
        obj.name = "linux"

        assert self.admin.custom_field_title(obj) == "torvalds/linux"

    def test_custom_field_title_short_description(self):
        """Test custom_field_title has correct short_description label."""
        assert self.admin.custom_field_title.short_description == "Name"

    # --- custom_field_github_url ---

    def test_custom_field_github_url_returns_anchor_tag(self):
        """Test custom_field_github_url returns an anchor tag with correct href."""
        obj = MagicMock()
        obj.owner.login = "OWASP"
        obj.name = "Nest"

        result = self.admin.custom_field_github_url(obj)

        assert "href" in result
        assert "https://github.com/OWASP/Nest" in result
        assert 'target="_blank"' in result
        assert "↗️" in result

    def test_custom_field_github_url_exact_html(self):
        """Test custom_field_github_url produces the expected exact HTML."""
        obj = MagicMock()
        obj.owner.login = "mock-owner"
        obj.name = "mock-repo"

        result = self.admin.custom_field_github_url(obj)
        expected = "<a href='https://github.com/mock-owner/mock-repo' target='_blank'>↗️</a>"

        assert result == expected

    def test_custom_field_github_url_short_description(self):
        """Test custom_field_github_url has correct short_description label."""
        assert self.admin.custom_field_github_url.short_description == "GitHub 🔗"
