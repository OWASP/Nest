"""Test cases for owasp_sync_project_levels management command."""

import json
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.db.models.base import ModelState

from apps.owasp.models.project import Project


class TestSyncProjectLevelsCommand:
    """Test suite for sync project levels command."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        yield

    def test_successful_sync_compliant_projects(self):
        """Test successful sync when projects are compliant with official levels."""
        official_data = [
            {"repo": "project-1", "level": 1.0},
            {"repo": "project-2", "level": 2.0},
        ]

        mock_project_1 = MagicMock(spec=Project)
        mock_project_1.key = "project-1"
        mock_project_1.level_raw = "1.0"
        mock_project_1.is_level_non_compliant = False
        mock_project_1._state = ModelState()

        mock_project_2 = MagicMock(spec=Project)
        mock_project_2.key = "project-2"
        mock_project_2.level_raw = "2.0"
        mock_project_2.is_level_non_compliant = False
        mock_project_2._state = ModelState()

        # Mock the manager
        mock_manager = MagicMock()
        mock_manager.all.return_value = [mock_project_1, mock_project_2]
        mock_manager.count.return_value = 2
        mock_manager.values_list.return_value = ["project-1", "project-2"]

        with patch(
            "apps.owasp.management.commands.owasp_sync_project_levels.get_repository_file_content",
            return_value=json.dumps(official_data),
        ), patch(
            "apps.owasp.models.project.Project.active_projects", mock_manager
        ), patch(
            "apps.owasp.models.project.Project.objects.bulk_update"
        ) as mock_bulk_update, patch(
            "sys.stdout", new=self.stdout
        ):
            call_command("owasp_sync_project_levels")

        # No changes expected since projects are already compliant
        mock_bulk_update.assert_not_called()
        output = self.stdout.getvalue()
        assert "No compliance status changes detected" in output

    def test_sync_non_compliant_projects(self):
        """Test sync when projects have non-matching levels."""
        official_data = [
            {"repo": "project-1", "level": 1.0},
            {"repo": "project-2", "level": 2.0},
        ]

        mock_project_1 = MagicMock(spec=Project)
        mock_project_1.key = "project-1"
        mock_project_1.level_raw = "2.0"  # Mismatch!
        mock_project_1.is_level_non_compliant = False
        mock_project_1._state = ModelState()

        mock_project_2 = MagicMock(spec=Project)
        mock_project_2.key = "project-2"
        mock_project_2.level_raw = "2.0"
        mock_project_2.is_level_non_compliant = False
        mock_project_2._state = ModelState()

        mock_manager = MagicMock()
        mock_manager.all.return_value = [mock_project_1, mock_project_2]
        mock_manager.count.return_value = 2
        mock_manager.values_list.return_value = ["project-1", "project-2"]

        with patch(
            "apps.owasp.management.commands.owasp_sync_project_levels.get_repository_file_content",
            return_value=json.dumps(official_data),
        ), patch(
            "apps.owasp.models.project.Project.active_projects", mock_manager
        ), patch(
            "apps.owasp.models.project.Project.objects.bulk_update"
        ) as mock_bulk_update, patch(
            "sys.stdout", new=self.stdout
        ):
            call_command("owasp_sync_project_levels")

        # Project 1 should be updated to non-compliant
        mock_bulk_update.assert_called_once()
        updated_projects = mock_bulk_update.call_args[0][0]
        assert len(updated_projects) == 1
        assert mock_project_1.is_level_non_compliant is True
        output = self.stdout.getvalue()
        assert "level mismatch" in output

    def test_sync_missing_from_official_list(self):
        """Test sync when project is missing from official levels."""
        official_data = [
            {"repo": "project-1", "level": 1.0},
        ]

        mock_project_1 = MagicMock(spec=Project)
        mock_project_1.key = "project-1"
        mock_project_1.level_raw = "1.0"
        mock_project_1.is_level_non_compliant = False
        mock_project_1._state = ModelState()

        mock_project_2 = MagicMock(spec=Project)
        mock_project_2.key = "project-2"
        mock_project_2.level_raw = "2.0"
        mock_project_2.is_level_non_compliant = False
        mock_project_2._state = ModelState()

        mock_manager = MagicMock()
        mock_manager.all.return_value = [mock_project_1, mock_project_2]
        mock_manager.count.return_value = 2
        mock_manager.values_list.return_value = ["project-1", "project-2"]

        with patch(
            "apps.owasp.management.commands.owasp_sync_project_levels.get_repository_file_content",
            return_value=json.dumps(official_data),
        ), patch(
            "apps.owasp.models.project.Project.active_projects", mock_manager
        ), patch(
            "apps.owasp.models.project.Project.objects.bulk_update"
        ) as mock_bulk_update, patch(
            "sys.stdout", new=self.stdout
        ):
            call_command("owasp_sync_project_levels")

        # Project 2 should be marked non-compliant (missing from official)
        mock_bulk_update.assert_called_once()
        updated_projects = mock_bulk_update.call_args[0][0]
        assert len(updated_projects) == 1
        assert mock_project_2.is_level_non_compliant is True
        output = self.stdout.getvalue()
        assert "missing from official OWASP project_levels.json" in output

    def test_sync_coverage_report(self):
        """Test that coverage report shows official projects not in Nest."""
        official_data = [
            {"repo": "project-1", "level": 1.0},
            {"repo": "project-2", "level": 2.0},
            {"repo": "official-only", "level": 3.0},
        ]

        mock_project_1 = MagicMock(spec=Project)
        mock_project_1.key = "project-1"
        mock_project_1.level_raw = "1.0"
        mock_project_1.is_level_non_compliant = False
        mock_project_1._state = ModelState()

        mock_manager = MagicMock()
        mock_manager.all.return_value = [mock_project_1]
        mock_manager.count.return_value = 1
        mock_manager.values_list.return_value = ["project-1"]

        with patch(
            "apps.owasp.management.commands.owasp_sync_project_levels.get_repository_file_content",
            return_value=json.dumps(official_data),
        ), patch(
            "apps.owasp.models.project.Project.active_projects", mock_manager
        ), patch(
            "apps.owasp.models.project.Project.objects.bulk_update"
        ), patch(
            "sys.stdout", new=self.stdout
        ):
            call_command("owasp_sync_project_levels")

        output = self.stdout.getvalue()
        # Should report 2 official projects not in Nest
        assert "2 official OWASP projects are not present in Nest" in output

    def test_failed_fetch_from_official_source(self):
        """Test handling when fetching official levels fails."""
        with patch(
            "apps.owasp.management.commands.owasp_sync_project_levels.get_repository_file_content",
            return_value=None,
        ), patch(
            "sys.stdout", new=self.stdout
        ):
            call_command("owasp_sync_project_levels")

        output = self.stdout.getvalue()
        assert "Failed to fetch project levels from OWASP GitHub repository" in output

    def test_json_parse_error(self):
        """Test handling when JSON parsing fails."""
        invalid_json = "{invalid json"

        with patch(
            "apps.owasp.management.commands.owasp_sync_project_levels.get_repository_file_content",
            return_value=invalid_json,
        ), patch(
            "sys.stdout", new=self.stdout
        ):
            call_command("owasp_sync_project_levels")

        output = self.stdout.getvalue()
        assert "Failed to parse project levels JSON" in output

    def test_incubator_level_handling(self):
        """Test that -1 level (incubator) is treated as valid."""
        official_data = [
            {"repo": "incubator-project", "level": -1.0},
        ]

        mock_project = MagicMock(spec=Project)
        mock_project.key = "incubator-project"
        mock_project.level_raw = "-1.0"
        mock_project.is_level_non_compliant = False
        mock_project._state = ModelState()

        mock_manager = MagicMock()
        mock_manager.all.return_value = [mock_project]
        mock_manager.count.return_value = 1
        mock_manager.values_list.return_value = ["incubator-project"]

        with patch(
            "apps.owasp.management.commands.owasp_sync_project_levels.get_repository_file_content",
            return_value=json.dumps(official_data),
        ), patch(
            "apps.owasp.models.project.Project.active_projects", mock_manager
        ), patch(
            "apps.owasp.models.project.Project.objects.bulk_update"
        ) as mock_bulk_update, patch(
            "sys.stdout", new=self.stdout
        ):
            call_command("owasp_sync_project_levels")

        # No changes expected, project is compliant
        mock_bulk_update.assert_not_called()
        output = self.stdout.getvalue()
        assert "No compliance status changes detected" in output

    def test_compliance_status_change_logged(self):
        """Test that compliance status changes are properly logged."""
        official_data = [
            {"repo": "project-1", "level": 1.0},
        ]

        # Project was previously non-compliant, now becomes compliant
        mock_project = MagicMock(spec=Project)
        mock_project.key = "project-1"
        mock_project.level_raw = "1.0"
        mock_project.is_level_non_compliant = True  # Currently marked non-compliant
        mock_project._state = ModelState()

        mock_manager = MagicMock()
        mock_manager.all.return_value = [mock_project]
        mock_manager.count.return_value = 1
        mock_manager.values_list.return_value = ["project-1"]

        with patch(
            "apps.owasp.management.commands.owasp_sync_project_levels.get_repository_file_content",
            return_value=json.dumps(official_data),
        ), patch(
            "apps.owasp.models.project.Project.active_projects", mock_manager
        ), patch(
            "apps.owasp.models.project.Project.objects.bulk_update"
        ) as mock_bulk_update, patch(
            "sys.stdout", new=self.stdout
        ):
            call_command("owasp_sync_project_levels")

        # Should update to compliant
        mock_bulk_update.assert_called_once()
        updated_projects = mock_bulk_update.call_args[0][0]
        assert len(updated_projects) == 1
        assert mock_project.is_level_non_compliant is False
        output = self.stdout.getvalue()
        assert "Updated 1 compliance status records" in output
