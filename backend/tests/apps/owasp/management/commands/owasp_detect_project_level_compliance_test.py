"""Tests for owasp_detect_project_level_compliance command."""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.db.models.base import ModelState

from apps.owasp.management.commands.owasp_detect_project_level_compliance import Command
from apps.owasp.models.project import Project

# Test constants
OWASP_ZAP_NAME = "OWASP ZAP"
OWASP_TEST_PROJECT_NAME = "OWASP Test Project"
OWASP_TOP_TEN_NAME = "OWASP Top 10"
PROJECT_FILTER_PATCH = "apps.owasp.models.project.Project.objects.filter"
STDOUT_PATCH = "sys.stdout"
FLAGSHIP_LEVEL = "flagship"
PRODUCTION_LEVEL = "production"
LAB_LEVEL = "lab"
OTHER_LEVEL = "other"
COMPLIANCE_SUMMARY_HEADER = "PROJECT LEVEL COMPLIANCE SUMMARY"
TOTAL_PROJECTS_PREFIX = "Total active projects:"
COMPLIANT_PROJECTS_PREFIX = "Compliant projects:"
NON_COMPLIANT_PROJECTS_PREFIX = "Non-compliant projects:"
COMPLIANCE_RATE_PREFIX = "Compliance rate:"
ALL_COMPLIANT_MESSAGE = "✓ All projects are level compliant!"
WARNING_PREFIX = "WARNING: Found"
INFO_PREFIX = "INFO:"
SUCCESS_CHECK = "✓"
ERROR_CHECK = "✗"


class TestDetectProjectLevelComplianceCommand:
    """Test cases for the project level compliance detection command."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        self.command = Command()

    def test_handle_all_compliant_projects(self):
        """Test command output when all projects are compliant."""
        # Create mock compliant projects
        project1 = MagicMock(spec=Project)
        project1._state = ModelState()
        project1.name = OWASP_ZAP_NAME
        project1.level = FLAGSHIP_LEVEL
        project1.project_level_official = FLAGSHIP_LEVEL
        project1.is_level_compliant = True

        project2 = MagicMock(spec=Project)
        project2._state = ModelState()
        project2.name = OWASP_TOP_TEN_NAME
        project2.level = FLAGSHIP_LEVEL
        project2.project_level_official = FLAGSHIP_LEVEL
        project2.is_level_compliant = True

        project3 = MagicMock(spec=Project)
        project3._state = ModelState()
        project3.name = OWASP_TEST_PROJECT_NAME
        project3.level = PRODUCTION_LEVEL
        project3.project_level_official = PRODUCTION_LEVEL
        project3.is_level_compliant = True

        projects = [project1, project2, project3]

        with patch(PROJECT_FILTER_PATCH) as mock_filter, patch(STDOUT_PATCH, new=self.stdout):
            mock_filter.return_value.select_related.return_value = projects

            call_command("owasp_detect_project_level_compliance")

            output = self.stdout.getvalue()

            # Verify summary output
            assert COMPLIANCE_SUMMARY_HEADER in output
            assert f"{TOTAL_PROJECTS_PREFIX} 3" in output
            assert f"{COMPLIANT_PROJECTS_PREFIX} 3" in output
            assert f"{NON_COMPLIANT_PROJECTS_PREFIX} 0" in output
            assert f"{COMPLIANCE_RATE_PREFIX} 100.0%" in output
            assert ALL_COMPLIANT_MESSAGE in output

    def test_handle_mixed_compliance_projects(self):
        """Test command output with both compliant and non-compliant projects."""
        # Create mixed compliance projects
        project1 = MagicMock(spec=Project)
        project1._state = ModelState()
        project1.name = OWASP_ZAP_NAME
        project1.level = FLAGSHIP_LEVEL
        project1.project_level_official = FLAGSHIP_LEVEL
        project1.is_level_compliant = True

        project2 = MagicMock(spec=Project)
        project2._state = ModelState()
        project2.name = OWASP_TEST_PROJECT_NAME
        project2.level = LAB_LEVEL
        project2.project_level_official = PRODUCTION_LEVEL
        project2.is_level_compliant = False

        project3 = MagicMock(spec=Project)
        project3._state = ModelState()
        project3.name = OWASP_TOP_TEN_NAME
        project3.level = PRODUCTION_LEVEL
        project3.project_level_official = FLAGSHIP_LEVEL
        project3.is_level_compliant = False

        projects = [project1, project2, project3]

        with patch(PROJECT_FILTER_PATCH) as mock_filter, patch(STDOUT_PATCH, new=self.stdout):
            mock_filter.return_value.select_related.return_value = projects

            call_command("owasp_detect_project_level_compliance")

            output = self.stdout.getvalue()

            # Verify summary output
            assert f"{TOTAL_PROJECTS_PREFIX} 3" in output
            assert f"{COMPLIANT_PROJECTS_PREFIX} 1" in output
            assert f"{NON_COMPLIANT_PROJECTS_PREFIX} 2" in output
            assert f"{COMPLIANCE_RATE_PREFIX} 33.3%" in output
            assert f"{WARNING_PREFIX} 2 non-compliant projects" in output

            # Verify non-compliant projects are listed
            error_msg1 = (
                f"{ERROR_CHECK} {OWASP_TEST_PROJECT_NAME}: "
                f"Local={LAB_LEVEL}, Official={PRODUCTION_LEVEL}"
            )
            assert error_msg1 in output
            error_msg2 = (
                f"{ERROR_CHECK} {OWASP_TOP_TEN_NAME}: "
                f"Local={PRODUCTION_LEVEL}, Official={FLAGSHIP_LEVEL}"
            )
            assert error_msg2 in output

    def test_handle_verbose_output(self):
        """Test command with verbose flag shows all projects."""
        project1 = MagicMock(spec=Project)
        project1._state = ModelState()
        project1.name = OWASP_ZAP_NAME
        project1.level = FLAGSHIP_LEVEL
        project1.project_level_official = FLAGSHIP_LEVEL
        project1.is_level_compliant = True

        project2 = MagicMock(spec=Project)
        project2._state = ModelState()
        project2.name = OWASP_TEST_PROJECT_NAME
        project2.level = LAB_LEVEL
        project2.project_level_official = PRODUCTION_LEVEL
        project2.is_level_compliant = False

        projects = [project1, project2]

        with patch(PROJECT_FILTER_PATCH) as mock_filter, patch(STDOUT_PATCH, new=self.stdout):
            mock_filter.return_value.select_related.return_value = projects

            call_command("owasp_detect_project_level_compliance", "--verbose")

            output = self.stdout.getvalue()

            # Verify both compliant and non-compliant projects are shown
            success_msg = f"{SUCCESS_CHECK} {OWASP_ZAP_NAME}: {FLAGSHIP_LEVEL} (matches official)"
            assert success_msg in output
            error_msg = (
                f"{ERROR_CHECK} {OWASP_TEST_PROJECT_NAME}: "
                f"Local={LAB_LEVEL}, Official={PRODUCTION_LEVEL}"
            )
            assert error_msg in output

    def test_handle_no_projects(self):
        """Test command output when no active projects exist."""
        with patch(PROJECT_FILTER_PATCH) as mock_filter, patch(STDOUT_PATCH, new=self.stdout):
            mock_filter.return_value.select_related.return_value = []

            call_command("owasp_detect_project_level_compliance")

            output = self.stdout.getvalue()

            # Verify summary for empty project list
            assert f"{TOTAL_PROJECTS_PREFIX} 0" in output
            assert f"{COMPLIANT_PROJECTS_PREFIX} 0" in output
            assert f"{NON_COMPLIANT_PROJECTS_PREFIX} 0" in output
            assert ALL_COMPLIANT_MESSAGE in output

    def test_handle_projects_without_official_levels(self):
        """Test command detects projects with default official levels."""
        project1 = MagicMock(spec=Project)
        project1._state = ModelState()
        project1.name = OWASP_ZAP_NAME
        project1.level = FLAGSHIP_LEVEL
        project1.project_level_official = FLAGSHIP_LEVEL
        project1.is_level_compliant = True

        project2 = MagicMock(spec=Project)
        project2._state = ModelState()
        project2.name = OWASP_TEST_PROJECT_NAME
        project2.level = LAB_LEVEL
        project2.project_level_official = OTHER_LEVEL  # Default official level
        project2.is_level_compliant = True

        projects = [project1, project2]

        with patch(PROJECT_FILTER_PATCH) as mock_filter, patch(STDOUT_PATCH, new=self.stdout):
            # Mock the filter for projects without official levels
            mock_filter.return_value.select_related.return_value = projects
            mock_filter.return_value.filter.return_value.count.return_value = 1

            call_command("owasp_detect_project_level_compliance")

            output = self.stdout.getvalue()

            # Verify info message about default official levels
            assert f"{INFO_PREFIX} 1 projects have default official levels" in output
            assert (
                "Run 'make update-data' to sync official levels, "
                "then 'make sync-data' for scoring." in output
            )

    def test_compliance_rate_calculation(self):
        """Test compliance rate calculation with various scenarios."""
        test_cases = [
            ([], 0, 0, 0.0),  # No projects
            ([True], 1, 0, 100.0),  # All compliant
            ([False], 0, 1, 0.0),  # All non-compliant
            ([True, False, True], 2, 1, 66.7),  # Mixed
        ]

        for (
            compliance_statuses,
            expected_compliant,
            expected_non_compliant,
            expected_rate,
        ) in test_cases:
            projects = []
            for i, is_compliant in enumerate(compliance_statuses):
                project = MagicMock(spec=Project)
                project._state = ModelState()
                project.name = f"Project {i}"
                project.level = LAB_LEVEL
                project.project_level_official = LAB_LEVEL if is_compliant else FLAGSHIP_LEVEL
                project.is_level_compliant = is_compliant
                projects.append(project)

            with (
                patch("apps.owasp.models.project.Project.objects.filter") as mock_filter,
                patch("sys.stdout", new=StringIO()) as mock_stdout,
            ):
                mock_filter.return_value.select_related.return_value = projects
                mock_filter.return_value.filter.return_value.count.return_value = 0

                call_command("owasp_detect_project_level_compliance")

                output = mock_stdout.getvalue()

                assert f"{COMPLIANT_PROJECTS_PREFIX} {expected_compliant}" in output
                assert f"{NON_COMPLIANT_PROJECTS_PREFIX} {expected_non_compliant}" in output
                assert f"{COMPLIANCE_RATE_PREFIX} {expected_rate:.1f}%" in output
