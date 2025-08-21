"""Tests for owasp_detect_project_level_compliance command."""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.db.models.base import ModelState

from apps.owasp.management.commands.owasp_detect_project_level_compliance import Command
from apps.owasp.models.project import Project


class TestDetectProjectLevelComplianceCommand:
    """Test cases for the project level compliance detection command."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        self.command = Command()
        yield

    def create_mock_project(self, name, level, official_level, is_compliant):
        """Helper to create a mock project."""
        project = MagicMock(spec=Project)
        project._state = ModelState()
        project.name = name
        project.level = level
        project.project_level_official = official_level
        project.is_level_compliant = is_compliant
        return project

    def test_handle_all_compliant_projects(self):
        """Test command output when all projects are compliant."""
        # Create mock compliant projects
        projects = [
            self.create_mock_project("OWASP ZAP", "flagship", "flagship", True),
            self.create_mock_project("OWASP Top 10", "flagship", "flagship", True),
            self.create_mock_project("OWASP WebGoat", "production", "production", True),
        ]

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter, \
             patch("sys.stdout", new=self.stdout):
            
            mock_filter.return_value.select_related.return_value = projects
            
            call_command("owasp_detect_project_level_compliance")
            
            output = self.stdout.getvalue()
            
            # Verify summary output
            assert "PROJECT LEVEL COMPLIANCE SUMMARY" in output
            assert "Total active projects: 3" in output
            assert "Compliant projects: 3" in output
            assert "Non-compliant projects: 0" in output
            assert "Compliance rate: 100.0%" in output
            assert "✓ All projects are level compliant!" in output

    def test_handle_mixed_compliance_projects(self):
        """Test command output with both compliant and non-compliant projects."""
        # Create mixed compliance projects
        projects = [
            self.create_mock_project("OWASP ZAP", "flagship", "flagship", True),
            self.create_mock_project("OWASP WebGoat", "lab", "production", False),
            self.create_mock_project("OWASP Top 10", "production", "flagship", False),
        ]

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter, \
             patch("sys.stdout", new=self.stdout):
            
            mock_filter.return_value.select_related.return_value = projects
            
            call_command("owasp_detect_project_level_compliance")
            
            output = self.stdout.getvalue()
            
            # Verify summary output
            assert "Total active projects: 3" in output
            assert "Compliant projects: 1" in output
            assert "Non-compliant projects: 2" in output
            assert "Compliance rate: 33.3%" in output
            assert "⚠ WARNING: Found 2 non-compliant projects" in output
            
            # Verify non-compliant projects are listed
            assert "✗ OWASP WebGoat: Local=lab, Official=production" in output
            assert "✗ OWASP Top 10: Local=production, Official=flagship" in output

    def test_handle_verbose_output(self):
        """Test command with verbose flag shows all projects."""
        projects = [
            self.create_mock_project("OWASP ZAP", "flagship", "flagship", True),
            self.create_mock_project("OWASP WebGoat", "lab", "production", False),
        ]

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter, \
             patch("sys.stdout", new=self.stdout):
            
            mock_filter.return_value.select_related.return_value = projects
            
            call_command("owasp_detect_project_level_compliance", "--verbose")
            
            output = self.stdout.getvalue()
            
            # Verify both compliant and non-compliant projects are shown
            assert "✓ OWASP ZAP: flagship (matches official)" in output
            assert "✗ OWASP WebGoat: Local=lab, Official=production" in output

    def test_handle_no_projects(self):
        """Test command output when no active projects exist."""
        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter, \
             patch("sys.stdout", new=self.stdout):
            
            mock_filter.return_value.select_related.return_value = []
            
            call_command("owasp_detect_project_level_compliance")
            
            output = self.stdout.getvalue()
            
            # Verify summary for empty project list
            assert "Total active projects: 0" in output
            assert "Compliant projects: 0" in output
            assert "Non-compliant projects: 0" in output
            assert "✓ All projects are level compliant!" in output

    def test_handle_projects_without_official_levels(self):
        """Test command detects projects with default official levels."""
        projects = [
            self.create_mock_project("OWASP ZAP", "flagship", "flagship", True),
            self.create_mock_project("OWASP WebGoat", "lab", "other", True),  # Default official level
        ]

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter, \
             patch("sys.stdout", new=self.stdout):
            
            # Mock the filter for projects without official levels
            mock_filter.return_value.select_related.return_value = projects
            mock_filter.return_value.filter.return_value.count.return_value = 1
            
            call_command("owasp_detect_project_level_compliance")
            
            output = self.stdout.getvalue()
            
            # Verify info message about default official levels
            assert "ℹ INFO: 1 projects have default official levels" in output
            assert "Run 'owasp_update_project_health_metrics' to sync official levels" in output

    def test_compliance_rate_calculation(self):
        """Test compliance rate calculation with various scenarios."""
        test_cases = [
            ([], 0, 0, 0.0),  # No projects
            ([True], 1, 0, 100.0),  # All compliant
            ([False], 0, 1, 0.0),  # All non-compliant
            ([True, False, True], 2, 1, 66.7),  # Mixed
        ]

        for compliance_statuses, expected_compliant, expected_non_compliant, expected_rate in test_cases:
            projects = [
                self.create_mock_project(f"Project {i}", "lab", "lab" if compliant else "flagship", compliant)
                for i, compliant in enumerate(compliance_statuses)
            ]

            with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter, \
                 patch("sys.stdout", new=StringIO()) as mock_stdout:
                
                mock_filter.return_value.select_related.return_value = projects
                mock_filter.return_value.filter.return_value.count.return_value = 0
                
                call_command("owasp_detect_project_level_compliance")
                
                output = mock_stdout.getvalue()
                
                assert f"Compliant projects: {expected_compliant}" in output
                assert f"Non-compliant projects: {expected_non_compliant}" in output
                assert f"Compliance rate: {expected_rate:.1f}%" in output