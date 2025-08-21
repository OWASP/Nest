from io import StringIO
from unittest.mock import MagicMock, patch
import json

import pytest
from django.core.management import call_command
from django.db.models.base import ModelState
import requests

from apps.owasp.management.commands.owasp_update_project_health_metrics import Command
from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


class TestUpdateProjectHealthMetricsCommand:
    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        self.command = Command()
        with (
            patch("apps.owasp.models.project.Project.objects.filter") as projects_patch,
            patch(
                "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.bulk_save"
            ) as bulk_save_patch,
        ):
            self.mock_projects = projects_patch
            self.mock_bulk_save = bulk_save_patch
            yield

    def test_handle_successful_update(self):
        """Test successful metrics update."""
        test_data = {
            "name": "Test Project",
            "contributors_count": 10,
            "created_at": "2023-01-01",
            "forks_count": 2,
            "is_funding_requirements_compliant": True,
            "released_at": "2023-02-01",
            "pushed_at": "2023-03-01",
            "open_issues_count": 1,
            "open_pull_requests_count": 1,
            "owasp_page_last_updated_at": "2023-04-01",
            "pull_request_last_created_at": "2023-05-01",
            "recent_releases_count": 1,
            "stars_count": 100,
            "issues_count": 5,
            "pull_requests_count": 3,
            "releases_count": 2,
            "unanswered_issues_count": 0,
            "unassigned_issues_count": 0,
        }

        # Create mock project with test data
        mock_project = MagicMock(spec=Project)
        mock_project._state = ModelState()
        for project_field, value in test_data.items():
            setattr(mock_project, project_field, value)

        self.mock_projects.return_value = [mock_project]

        # Set the leaders count to meet compliance
        mock_project.leaders_count = 2

        # Execute command
        with patch("sys.stdout", new=self.stdout):
            call_command("owasp_update_project_health_metrics")

        self.mock_bulk_save.assert_called_once()
        saved_metrics = self.mock_bulk_save.call_args[0][0]
        assert len(saved_metrics) == 1
        metrics = saved_metrics[0]
        assert isinstance(metrics, ProjectHealthMetrics)
        assert metrics.project == mock_project

        # Verify command output
        assert "Evaluating metrics for project: Test Project" in self.stdout.getvalue()

    @patch('requests.get')
    def test_fetch_official_project_levels_success(self, mock_get):
        """Test successful fetching of official project levels."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "OWASP ZAP", "level": "flagship"},
            {"name": "OWASP Top 10", "level": "flagship"},
            {"name": "OWASP WebGoat", "level": "production"},
            {"name": "Test Project", "level": "lab"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.command.fetch_official_project_levels(timeout=30)

        assert result is not None
        assert len(result) == 4
        assert result["OWASP ZAP"] == "flagship"
        assert result["OWASP Top 10"] == "flagship"
        assert result["OWASP WebGoat"] == "production"
        assert result["Test Project"] == "lab"

        # Verify API call
        mock_get.assert_called_once_with(
            "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/project_levels.json",
            timeout=30,
            headers={"Accept": "application/json"}
        )

    @patch('requests.get')
    def test_fetch_official_project_levels_http_error(self, mock_get):
        """Test handling of HTTP errors when fetching official levels."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = self.command.fetch_official_project_levels(timeout=30)

        assert result is None

    @patch('requests.get')
    def test_fetch_official_project_levels_invalid_json(self, mock_get):
        """Test handling of invalid JSON response."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.command.fetch_official_project_levels(timeout=30)

        assert result is None

    @patch('requests.get')
    def test_fetch_official_project_levels_invalid_format(self, mock_get):
        """Test handling of invalid data format (not a list)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "Invalid format"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.command.fetch_official_project_levels(timeout=30)

        assert result is None

    @patch('requests.get')
    def test_fetch_official_project_levels_filters_invalid_entries(self, mock_get):
        """Test that invalid entries are filtered out."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "Valid Project", "level": "flagship"},
            {"name": "", "level": "lab"},  # Empty name should be filtered
            {"level": "production"},  # Missing name should be filtered
            {"name": "Another Valid", "level": "incubator"},
            {"name": "Valid with number", "level": 3},  # Number level should work
            {"name": "Invalid level"},  # Missing level should be filtered
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.command.fetch_official_project_levels(timeout=30)

        assert result is not None
        assert len(result) == 3
        assert result["Valid Project"] == "flagship"
        assert result["Another Valid"] == "incubator"
        assert result["Valid with number"] == "3"

    def test_update_official_levels_success(self):
        """Test successful update of official levels."""
        # Create mock projects
        project1 = MagicMock(spec=Project)
        project1.name = "OWASP ZAP"
        project1.project_level_official = "lab"  # Different from official
        project1._state = ModelState()

        project2 = MagicMock(spec=Project)
        project2.name = "OWASP Top 10"
        project2.project_level_official = "flagship"  # Same as official
        project2._state = ModelState()

        official_levels = {
            "OWASP ZAP": "flagship",
            "OWASP Top 10": "flagship",
        }

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter, \
             patch("apps.owasp.models.project.Project.bulk_save") as mock_bulk_save:
            
            mock_filter.return_value = [project1, project2]
            
            updated_count = self.command.update_official_levels(official_levels)
            
            # Only project1 should be updated (different level)
            assert updated_count == 1
            assert project1.project_level_official == "flagship"
            assert project2.project_level_official == "flagship"  # Unchanged
            
            # Verify bulk_save was called with only the updated project
            mock_bulk_save.assert_called_once()
            saved_projects = mock_bulk_save.call_args[0][0]
            assert len(saved_projects) == 1
            assert saved_projects[0] == project1

    def test_update_official_levels_level_mapping(self):
        """Test that level mapping works correctly."""
        project = MagicMock(spec=Project)
        project.name = "Test Project"
        project.project_level_official = "other"
        project._state = ModelState()

        test_cases = [
            ("2", "incubator"),
            ("3", "lab"),
            ("3.5", "production"),
            ("4", "flagship"),
            ("incubator", "incubator"),
            ("lab", "lab"),
            ("production", "production"),
            ("flagship", "flagship"),
            ("unknown", "other"),
        ]

        for official_level, expected_mapped in test_cases:
            with patch("apps.owasp.models.project.Project.objects.filter") as mock_filter, \
                 patch("apps.owasp.models.project.Project.bulk_save") as mock_bulk_save:
                
                mock_filter.return_value = [project]
                project.project_level_official = "other"  # Reset
                
                official_levels = {"Test Project": official_level}
                self.command.update_official_levels(official_levels)
                
                assert project.project_level_official == expected_mapped

    @patch('requests.get')
    def test_handle_with_official_levels_integration(self, mock_get):
        """Test complete integration with official levels fetching."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "Test Project", "level": "flagship"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock project
        mock_project = MagicMock(spec=Project)
        mock_project._state = ModelState()
        mock_project.name = "Test Project"
        mock_project.project_level_official = "lab"  # Different from official
        for field in ["contributors_count", "created_at", "forks_count",
                     "is_funding_requirements_compliant", "is_leader_requirements_compliant",
                     "pushed_at", "released_at", "open_issues_count", "open_pull_requests_count",
                     "owasp_page_last_updated_at", "pull_request_last_created_at",
                     "recent_releases_count", "stars_count", "issues_count",
                     "pull_requests_count", "releases_count", "unanswered_issues_count",
                     "unassigned_issues_count"]:
            setattr(mock_project, field, 0)

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_projects, \
             patch("apps.owasp.models.project.Project.bulk_save") as mock_project_bulk_save, \
             patch("apps.owasp.models.project_health_metrics.ProjectHealthMetrics.bulk_save") as mock_metrics_bulk_save, \
             patch("sys.stdout", new=self.stdout):
            
            mock_projects.return_value = [mock_project]
            
            call_command("owasp_update_project_health_metrics")
            
            # Verify official levels were fetched and updated
            assert "Fetching official project levels" in self.stdout.getvalue()
            assert "Successfully fetched 1 official project levels" in self.stdout.getvalue()
            assert "Updated official levels for 1 projects" in self.stdout.getvalue()
            
            # Verify project was updated with official level
            assert mock_project.project_level_official == "flagship"
            mock_project_bulk_save.assert_called()
            mock_metrics_bulk_save.assert_called()

    def test_handle_skip_official_levels(self):
        """Test command with --skip-official-levels flag."""
        mock_project = MagicMock(spec=Project)
        mock_project._state = ModelState()
        mock_project.name = "Test Project"
        for field in ["contributors_count", "created_at", "forks_count",
                     "is_funding_requirements_compliant", "is_leader_requirements_compliant",
                     "pushed_at", "released_at", "open_issues_count", "open_pull_requests_count",
                     "owasp_page_last_updated_at", "pull_request_last_created_at",
                     "recent_releases_count", "stars_count", "issues_count",
                     "pull_requests_count", "releases_count", "unanswered_issues_count",
                     "unassigned_issues_count"]:
            setattr(mock_project, field, 0)

        with patch("apps.owasp.models.project.Project.objects.filter") as mock_projects, \
             patch("apps.owasp.models.project_health_metrics.ProjectHealthMetrics.bulk_save") as mock_bulk_save, \
             patch("sys.stdout", new=self.stdout):
            
            mock_projects.return_value = [mock_project]
            
            call_command("owasp_update_project_health_metrics", "--skip-official-levels")
            
            # Verify official levels fetching was skipped
            output = self.stdout.getvalue()
            assert "Fetching official project levels" not in output
            assert "Evaluating metrics for project: Test Project" in output
            mock_bulk_save.assert_called()
