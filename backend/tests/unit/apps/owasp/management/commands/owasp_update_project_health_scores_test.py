from datetime import timedelta
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.owasp.management.commands.owasp_update_project_health_scores import Command
from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements

EXPECTED_SCORE = 34.0
MAX_SCORE = 100.0
MISSING_DATES_WEIGHT = 24.0
REQUIREMENT_DAYS = 365


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

    @pytest.mark.parametrize(
        ("project_age_days", "expected_score"),
        [
            (REQUIREMENT_DAYS - 1, MAX_SCORE),
            (REQUIREMENT_DAYS, MAX_SCORE),
            (REQUIREMENT_DAYS + 1, MAX_SCORE - MISSING_DATES_WEIGHT),
            (None, MAX_SCORE - MISSING_DATES_WEIGHT),
        ],
    )
    def test_handle_counts_missing_dates_from_project_start(
        self, project_age_days, expected_score
    ):
        """Test missing activity dates earn points only within the project's first days."""
        project = Project(name="Test Project", level="lab")
        metric = ProjectHealthMetrics(
            created_at=project_age_days and timezone.now() - timedelta(days=project_age_days),
            is_funding_requirements_compliant=True,
            is_leader_requirements_compliant=True,
            project=project,
        )
        requirements = ProjectHealthRequirements(
            last_commit_days=REQUIREMENT_DAYS,
            last_pull_request_days=REQUIREMENT_DAYS,
            last_release_days=REQUIREMENT_DAYS,
            level=project.level,
            owasp_page_last_update_days=REQUIREMENT_DAYS,
        )
        self.mock_metrics.return_value.select_related.return_value = [metric]
        self.mock_requirements.return_value = [requirements]

        call_command("owasp_update_project_health_scores", stdout=self.stdout)

        assert metric.score == expected_score
