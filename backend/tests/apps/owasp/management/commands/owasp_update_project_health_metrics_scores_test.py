from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command

from apps.owasp.management.commands.owasp_update_project_health_metrics_scores import Command
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements


class TestUpdateProjectHealthMetricsScoreCommand:
    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        self.command = Command()
        with (
            patch(
                "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.objects.filter"
            ) as metrics_patch,
            patch(
                "apps.owasp.models.project_health_requirements.ProjectHealthRequirements.objects.get"
            ) as requirements_patch,
            patch(
                "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.bulk_save"
            ) as bulk_save_patch,
        ):
            self.mock_metrics = metrics_patch
            self.mock_requirements = requirements_patch
            self.mock_bulk_save = bulk_save_patch
            yield

    def test_handle_successful_update(self):
        """Test successful metrics score update."""
        # field -> requirements weight, metrics weight
        fields_weights = {
            "age_days": 3.0,
            "contributors_count": 3.0,
            "forks_count": 3.0,
            "last_release_days": 3.0,
            "last_commit_days": 3.0,
            "open_issues_count": 3.0,
            "open_pull_requests_count": 3.0,
            "owasp_page_last_update_days": 3.0,
            "last_pull_request_days": 3.0,
            "recent_releases_count": 3.0,
            "stars_count": 4.0,
            "total_pull_requests_count": 4.0,
            "total_releases_count": 4.0,
            "unanswered_issues_count": 4.0,
            "unassigned_issues_count": 4.0,
        }

        # Create mock metrics with test data
        mock_metric = MagicMock(spec=ProjectHealthMetrics)
        for field, weight in fields_weights.items():
            setattr(mock_metric, field, weight)
        mock_metric.project.level = "test_level"
        mock_metric.project.name = "Test Project"
        self.mock_metrics.return_value = [mock_metric]

        mock_requirements = MagicMock(spec=ProjectHealthRequirements)
        for field, weight in fields_weights.items():
            setattr(mock_requirements, field, weight)
        self.mock_requirements.return_value = mock_requirements
        mock_requirements.level = "test_level"

        expected_score = sum(weight for weight in fields_weights.values())
        mock_metric.score = expected_score
        # Execute command
        with patch("sys.stdout", new=self.stdout):
            call_command("owasp_update_project_health_metrics_scores")

        self.mock_requirements.assert_called_once_with(level=mock_metric.project.level)
        # Check if score was calculated correctly

        assert "Updated projects health metrics score successfully." in self.stdout.getvalue()
        assert "Updating score for project: Test Project" in self.stdout.getvalue()
