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
