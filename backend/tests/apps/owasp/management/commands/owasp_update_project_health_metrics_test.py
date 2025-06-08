from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.db.models.base import ModelState

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
            patch("apps.owasp.models.project.Project.objects.all") as projects_patch,
            patch(
                "apps.owasp.models.project_health_metrics.ProjectHealthMetrics"
            ) as metrics_patch,
            patch(
                "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.bulk_save"
            ) as bulk_save_patch,
        ):
            self.mock_projects = projects_patch
            self.mock_metrics = metrics_patch
            self.mock_bulk_save = bulk_save_patch
            yield

    def test_handle_successful_update(self):
        """Test successful metrics update."""
        # Define test data with mapping between project and metrics fields
        test_data = {
            # Project field -> Expected metrics field and value
            "name": ("name", "Test Project"),
            "contributors_count": ("contributors_count", 10),
            "created_at": ("created_at", "2023-01-01"),
            "forks_count": ("forks_count", 2),
            "is_funding_requirements_compliant": ("is_funding_requirements_compliant", True),
            "released_at": ("last_released_at", "2023-02-01"),
            "pushed_at": ("last_committed_at", "2023-03-01"),
            "open_issues_count": ("open_issues_count", 1),
            "open_pull_requests_count": ("open_pull_requests_count", 1),
            "owasp_page_last_updated_at": ("owasp_page_last_updated_at", "2023-04-01"),
            "pull_request_last_created_at": ("pull_request_last_created_at", "2023-05-01"),
            "recent_releases_count": ("recent_releases_count", 1),
            "stars_count": ("stars_count", 100),
            "issues_count": ("total_issues_count", 5),
            "pull_requests_count": ("total_pull_requests_count", 3),
            "releases_count": ("total_releases_count", 2),
            "unanswered_issues_count": ("unanswered_issues_count", 0),
            "unassigned_issues_count": ("unassigned_issues_count", 0),
        }

        # Create mock project with test data
        mock_project = MagicMock(spec=Project)
        mock_project._state = ModelState()
        for project_field, (_, value) in test_data.items():
            setattr(mock_project, project_field, value)

        self.mock_projects.return_value = [mock_project]

        mock_metrics_instance = MagicMock(spec=ProjectHealthMetrics)
        mock_metrics_instance._state = ModelState()
        self.mock_metrics.return_value = mock_metrics_instance
        # Set the leaders count to meet compliance
        mock_project.leaders_count = 2
        mock_metrics_instance.is_project_leaders_requirements_compliant = True

        # Execute command
        with patch("sys.stdout", new=self.stdout):
            call_command("owasp_update_project_health_metrics")

        # Verify command output
        assert "Evaluating metrics for project: Test Project" in self.stdout.getvalue()

    def test_handle_empty_projects(self):
        """Test command with no projects."""
        self.mock_projects.return_value = []

        with patch("sys.stdout", new=self.stdout):
            call_command("owasp_update_project_health_metrics")

        output = self.stdout.getvalue()
        assert "Evaluated projects health metrics successfully" in output
