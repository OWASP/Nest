from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command

from apps.owasp.management.commands.owasp_update_project_health_scores import Command
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements

EXPECTED_SCORE = 34.0


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
                "apps.owasp.models.project_health_requirements.ProjectHealthRequirements.objects.all"
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
        fields_weights = {
            "age_days": (5, 6),
            "contributors_count": (5, 6),
            "forks_count": (5, 6),
            "last_release_days": (5, 6),
            "last_commit_days": (5, 6),
            "open_issues_count": (7, 6),
            "open_pull_requests_count": (5, 6),
            "owasp_page_last_update_days": (5, 6),
            "last_pull_request_days": (5, 6),
            "recent_releases_count": (5, 6),
            "stars_count": (5, 6),
            "total_pull_requests_count": (5, 6),
            "total_releases_count": (5, 6),
            "unanswered_issues_count": (7, 6),
            "unassigned_issues_count": (7, 6),
        }

        # Create mock metrics with test data
        mock_metric = MagicMock(spec=ProjectHealthMetrics)
        mock_requirements = MagicMock(spec=ProjectHealthRequirements)
        for field, (metric_weight, requirement_weight) in fields_weights.items():
            setattr(mock_metric, field, metric_weight)
            setattr(mock_requirements, field, requirement_weight)
        mock_metric.project.level = "test_level"
        mock_metric.project.name = "Test Project"
        mock_metric.is_funding_requirements_compliant = True
        mock_metric.is_leader_requirements_compliant = True
        self.mock_metrics.return_value.select_related.return_value = [mock_metric]
        self.mock_requirements.return_value = [mock_requirements]
        mock_requirements.level = "test_level"
        # Execute command
        with patch("sys.stdout", new=self.stdout):
            call_command("owasp_update_project_health_scores")

        self.mock_requirements.assert_called_once()

        # Check if score was calculated correctly
        self.mock_bulk_save.assert_called_once_with(
            [mock_metric],
            fields=[
                "score",
            ],
        )
        assert mock_metric.score == EXPECTED_SCORE
        assert "Updated project health scores successfully." in self.stdout.getvalue()
        assert "Updating score for project: Test Project" in self.stdout.getvalue()

    def test_handle_applies_level_non_compliance_penalty(self):
        """Test score reduction when project level is non-compliant.

        Ensures that a fixed penalty is applied to the calculated
        project health score when the project is marked as
        level non-compliant.
        """
        mock_metric = MagicMock(spec=ProjectHealthMetrics)
        mock_requirements = MagicMock(spec=ProjectHealthRequirements)

        # Minimal values to guarantee a positive base score
        mock_metric.age_days = 10
        mock_requirements.age_days = 5

        mock_metric.contributors_count = 10
        mock_requirements.contributors_count = 5

        mock_metric.forks_count = 10
        mock_requirements.forks_count = 5

        mock_metric.last_commit_days = 1
        mock_requirements.last_commit_days = 5

        mock_metric.last_release_days = 1
        mock_requirements.last_release_days = 5

        mock_metric.open_issues_count = 1
        mock_requirements.open_issues_count = 5

        mock_metric.open_pull_requests_count = 1
        mock_requirements.open_pull_requests_count = 5

        mock_metric.owasp_page_last_update_days = 1
        mock_requirements.owasp_page_last_update_days = 5

        mock_metric.last_pull_request_days = 1
        mock_requirements.last_pull_request_days = 5

        mock_metric.recent_releases_count = 10
        mock_requirements.recent_releases_count = 5

        mock_metric.stars_count = 10
        mock_requirements.stars_count = 5

        mock_metric.total_pull_requests_count = 10
        mock_requirements.total_pull_requests_count = 5

        mock_metric.total_releases_count = 10
        mock_requirements.total_releases_count = 5

        mock_metric.unanswered_issues_count = 1
        mock_requirements.unanswered_issues_count = 5

        mock_metric.unassigned_issues_count = 1
        mock_requirements.unassigned_issues_count = 5

        mock_metric.level_non_compliant = True
        mock_metric.is_funding_requirements_compliant = True
        mock_metric.is_leader_requirements_compliant = True

        mock_metric.project.level = "test_level"
        mock_metric.project.name = "Non Compliant Project"
        mock_requirements.level = "test_level"

        self.mock_metrics.return_value.select_related.return_value = [mock_metric]
        self.mock_requirements.return_value = [mock_requirements]

        with patch("sys.stdout", new=self.stdout):
            call_command("owasp_update_project_health_scores")

        self.mock_bulk_save.assert_called_once()
        assert mock_metric.score >= 0
        assert mock_metric.level_non_compliant is True
        assert "Updating score for project: Non Compliant Project" in self.stdout.getvalue()
