"""Tests for ProjectHealthMetrics admin."""

from unittest.mock import Mock

from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.project_health_metrics import ProjectHealthMetricsAdmin
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


class TestProjectHealthMetricsAdmin:
    """Tests for ProjectHealthMetricsAdmin."""

    def test_project_display_with_project(self):
        """Test project method returns project name when project exists."""
        admin = ProjectHealthMetricsAdmin(ProjectHealthMetrics, AdminSite())

        obj = Mock()
        obj.project = Mock()
        obj.project.name = "OWASP Top 10"

        result = admin.project(obj)
        assert result == "OWASP Top 10"

    def test_project_display_without_project(self):
        """Test project method returns 'N/A' when project is None."""
        admin = ProjectHealthMetricsAdmin(ProjectHealthMetrics, AdminSite())

        obj = Mock()
        obj.project = None

        result = admin.project(obj)
        assert result == "N/A"

    def test_list_display_includes_project(self):
        """Test list_display includes project method."""
        admin = ProjectHealthMetricsAdmin(ProjectHealthMetrics, AdminSite())
        assert "project" in admin.list_display

    def test_autocomplete_fields(self):
        """Test autocomplete_fields includes project."""
        admin = ProjectHealthMetricsAdmin(ProjectHealthMetrics, AdminSite())
        assert "project" in admin.autocomplete_fields

    def test_list_filter(self):
        """Test list_filter includes project level and created_at."""
        admin = ProjectHealthMetricsAdmin(ProjectHealthMetrics, AdminSite())
        assert "project__level" in admin.list_filter
        assert "nest_created_at" in admin.list_filter

    def test_search_fields(self):
        """Test search_fields includes project name."""
        admin = ProjectHealthMetricsAdmin(ProjectHealthMetrics, AdminSite())
        assert "project__name" in admin.search_fields
