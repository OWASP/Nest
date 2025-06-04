from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command

from apps.owasp.management.commands.owasp_update_project_health_metrics import Command
from apps.owasp.models.project import Project


class TestUpdateProjectHealthMetricsCommand:
    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        self.command = Command()
        with (
            patch("apps.owasp.models.project.Project.objects.all") as projects_patch,
            patch(
                "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.objects.get_or_create"
            ) as metrics_patch,
        ):
            self.mock_projects = projects_patch
            self.mock_metrics = metrics_patch
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
        for project_field, (_, value) in test_data.items():
            setattr(mock_project, project_field, value)

        self.mock_projects.return_value = [mock_project]

        # Execute command
        with patch("sys.stdout", new=self.stdout):
            call_command("owasp_update_project_health_metrics")

        # Verify command output
        assert "Updating metrics for project: Test Project" in self.stdout.getvalue()

        # Verify mock was called correctly
        self.mock_metrics.assert_called_once_with(project=mock_project)

        # Get the mocked metrics object
        metrics = self.mock_metrics.return_value[0]

        # Verify all field mappings
        for metrics_field, expected_value in test_data.values():
            # Skip name field as it's not in metrics
            if metrics_field != "name":
                actual_value = getattr(metrics, metrics_field)
                assert actual_value == expected_value, (
                    f"Field {metrics_field}: expected {expected_value}, got {actual_value}"
                )

    def test_handle_empty_projects(self):
        """Test command with no projects."""
        self.mock_projects.return_value = []

        with patch("sys.stdout", new=self.stdout):
            call_command("owasp_update_project_health_metrics")

        output = self.stdout.getvalue()
        assert "Updated 0 projects health metrics successfully" in output
        assert "Encountered errors for 0 projects" in output
