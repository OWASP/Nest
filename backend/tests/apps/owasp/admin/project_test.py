"""Tests for Project admin."""

from unittest.mock import Mock

from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.project import ProjectAdmin
from apps.owasp.models.project import Project


class TestProjectAdmin:
    """Tests for ProjectAdmin."""

    def test_custom_field_name_with_name(self):
        """Test custom_field_name returns project name when available."""
        admin = ProjectAdmin(Project, AdminSite())

        obj = Mock()
        obj.name = "OWASP Top 10"
        obj.key = "www-project-top-ten"

        result = admin.custom_field_name(obj)
        assert result == "OWASP Top 10"

    def test_custom_field_name_without_name(self):
        """Test custom_field_name returns key when name is empty."""
        admin = ProjectAdmin(Project, AdminSite())

        obj = Mock()
        obj.name = None
        obj.key = "www-project-example"

        result = admin.custom_field_name(obj)
        assert result == "www-project-example"

    def test_custom_field_name_with_empty_string_name(self):
        """Test custom_field_name returns key when name is empty string."""
        admin = ProjectAdmin(Project, AdminSite())

        obj = Mock()
        obj.name = ""
        obj.key = "www-project-test"

        result = admin.custom_field_name(obj)
        assert result == "www-project-test"

    def test_custom_field_name_short_description(self):
        """Test custom_field_name has correct short_description."""
        admin = ProjectAdmin(Project, AdminSite())
        assert admin.custom_field_name.short_description == "Name"

    def test_list_display_includes_custom_field_name(self):
        """Test list_display includes custom_field_name."""
        admin = ProjectAdmin(Project, AdminSite())
        assert "custom_field_name" in admin.list_display

    def test_ordering(self):
        """Test ordering is set correctly."""
        admin = ProjectAdmin(Project, AdminSite())
        assert admin.ordering == ("-created_at",)
