from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from reportlab.lib.pagesizes import letter

from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


class TestProjectHealthMetricsModel:
    DEFAULT_SCORE = None
    VALID_SCORE = 75.0
    MAX_SCORE = 100.0
    MIN_SCORE = 0.0
    FIXED_DATE = timezone.make_aware(
        timezone.datetime(2025, 1, 1), timezone.get_default_timezone()
    )

    @pytest.fixture
    def mock_project(self):
        """Mock a Project instance with simulated persistence."""
        project = Project(key="test_project", name="Test Project")
        project.pk = 1
        return project

    @pytest.mark.parametrize(
        ("project_name", "expected"),
        [
            ("Secure Project", "Health Metrics for Secure Project"),
            ("", "Health Metrics for "),
            (None, "Health Metrics for None"),
        ],
    )
    def test_str_representation(self, mock_project, project_name, expected):
        """Should return correct string representation."""
        mock_project.name = project_name
        metrics = ProjectHealthMetrics(project=mock_project)
        assert str(metrics) == expected

    @pytest.mark.parametrize(
        ("score", "is_valid"),
        [
            (VALID_SCORE, True),
            (MAX_SCORE, True),
            (MIN_SCORE, True),
            (MAX_SCORE + 0.1, False),
            (MIN_SCORE - 10.0, False),
        ],
    )
    def test_score_validation(self, score, is_valid):
        """Should validate score within allowed range."""
        metrics = ProjectHealthMetrics(score=score)

        if is_valid:
            metrics.clean_fields(exclude=["project"])
            assert metrics.score == score
        else:
            with pytest.raises(ValidationError) as exc_info:
                metrics.clean_fields(exclude=["project"])
            assert "score" in exc_info.value.error_dict

    def test_default_score(self):
        """Should initialize with default score value."""
        metrics = ProjectHealthMetrics()
        assert metrics.score == self.DEFAULT_SCORE

    @pytest.mark.parametrize(
        ("field_name", "expected_default"),
        [
            ("age_days", 0),
            ("contributors_count", 0),
            ("forks_count", 0),
            ("is_funding_requirements_compliant", False),
            ("is_leader_requirements_compliant", False),
            ("last_committed_at", None),
            ("last_commit_days", 0),
            ("last_pull_request_days", 0),
            ("last_released_at", None),
            ("last_release_days", 0),
            ("open_issues_count", 0),
            ("open_pull_requests_count", 0),
            ("owasp_page_last_updated_at", None),
            ("owasp_page_last_update_days", 0),
            ("pull_request_last_created_at", None),
            ("recent_releases_count", 0),
            ("score", None),
            ("stars_count", 0),
            ("total_issues_count", 0),
            ("total_pull_requests_count", 0),
            ("total_releases_count", 0),
            ("unanswered_issues_count", 0),
            ("unassigned_issues_count", 0),
        ],
    )
    def test_count_defaults(self, field_name, expected_default):
        """Should initialize count fields with proper defaults."""
        metrics = ProjectHealthMetrics()
        assert getattr(metrics, field_name) == expected_default

    @pytest.mark.parametrize(
        ("field_name", "expected_days"),
        [
            ("age_days", (timezone.now() - FIXED_DATE).days),
            ("last_commit_days", (timezone.now() - FIXED_DATE).days),
            ("last_pull_request_days", (timezone.now() - FIXED_DATE).days),
            ("last_release_days", (timezone.now() - FIXED_DATE).days),
            ("owasp_page_last_update_days", (timezone.now() - FIXED_DATE).days),
        ],
    )
    def test_handle_days_calculation(self, field_name, expected_days):
        """Should return correct days for date fields."""
        metrics = ProjectHealthMetrics()
        metrics.created_at = self.FIXED_DATE
        metrics.last_committed_at = self.FIXED_DATE
        metrics.last_released_at = self.FIXED_DATE
        metrics.owasp_page_last_updated_at = self.FIXED_DATE
        metrics.pull_request_last_created_at = self.FIXED_DATE

        assert getattr(metrics, field_name) == expected_days

    @patch(
        "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_latest_health_metrics",
    )
    @patch("apps.owasp.models.project_health_metrics.Canvas")
    @patch("apps.owasp.utils.Table")
    @patch("apps.owasp.utils.TableStyle")
    @patch("apps.owasp.models.project_health_metrics.BytesIO")
    def test_generate_detailed_pdf(
        self,
        mock_bytes_io,
        mock_table_style,
        mock_table,
        mock_canvas,
        mock_get_latest_health_metrics,
    ):
        metrics = MagicMock(
            age_days=30,
            contributors_count=20,
            forks_count=15,
            is_funding_requirements_compliant=True,
            is_leader_requirements_compliant=True,
            last_commit_days=5,
            last_commit_days_requirement=7,
            last_pull_request_days=2,
            last_release_days=10,
            last_release_days_requirement=14,
            open_issues_count=10,
            open_pull_requests_count=3,
            owasp_page_last_update_days=20,
            project=MagicMock(name="Test Project", key="www-project-test"),
            recent_releases_count=1,
            score=85.0,
            stars_count=100,
            total_issues_count=20,
            total_pull_requests_count=8,
            total_releases_count=10,
            unanswered_issues_count=2,
            unassigned_issues_count=5,
        )
        mock_get_latest_health_metrics.return_value.filter.return_value.first.return_value = (
            metrics
        )
        ProjectHealthMetrics.generate_latest_metrics_pdf("test")
        mock_bytes_io.assert_called_once()
        mock_canvas.assert_called_once_with(mock_bytes_io.return_value, pagesize=letter)
        canvas = mock_canvas.return_value
        table_data = [
            ["Metric", "Value"],
            ["Project Age", f"{metrics.age_days}/{metrics.age_days_requirement} days"],
            [
                "Last Commit",
                f"{metrics.last_commit_days}/{metrics.last_commit_days_requirement} days",
            ],
            [
                "Last Pull Request",
                # To bypass ruff long line error
                "/".join(
                    [
                        str(metrics.last_pull_request_days),
                        f"{metrics.last_pull_request_days_requirement} days",
                    ]
                ),
            ],
            [
                "Last Release",
                f"{metrics.last_release_days}/{metrics.last_release_days_requirement} days",
            ],
            [
                "OWASP Page Last Update",
                # To bypass ruff long line error
                "/".join(
                    [
                        str(metrics.owasp_page_last_update_days),
                        f"{metrics.owasp_page_last_update_days_requirement} days",
                    ]
                ),
            ],
            ["Open/Total Issues", f"{metrics.open_issues_count}/{metrics.total_issues_count}"],
            [
                "Open/Total Pull Requests",
                f"{metrics.open_pull_requests_count}/{metrics.total_pull_requests_count}",
            ],
            [
                "Recent/Total Releases",
                f"{metrics.recent_releases_count}/{metrics.total_releases_count}",
            ],
            ["Forks", metrics.forks_count],
            ["Stars", metrics.stars_count],
            [
                "Unassigned/Unanswered Issues",
                f"{metrics.unassigned_issues_count}/{metrics.unanswered_issues_count}",
            ],
            ["Contributors", metrics.contributors_count],
            [
                "Has funding policy issues",
                "No" if metrics.is_funding_requirements_compliant else "Yes",
            ],
            [
                "Has leadership policy issues",
                "No" if metrics.is_leader_requirements_compliant else "Yes",
            ],
        ]
        mock_table.assert_called_once_with(
            table_data, colWidths="*", style=mock_table_style.return_value
        )
        mock_table_style.assert_called_once()

        mock_table.return_value.wrapOn.assert_called_once_with(canvas, 500, 250)
        mock_table.return_value.drawOn.assert_called_once_with(canvas, 50, 220)
        canvas.showPage.assert_called_once()
        canvas.save.assert_called_once()

    @patch("apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_stats")
    @patch("apps.owasp.models.project_health_metrics.Canvas")
    @patch("apps.owasp.utils.Table")
    @patch("apps.owasp.utils.TableStyle")
    @patch("apps.owasp.models.project_health_metrics.BytesIO")
    def test_generate_overview_pdf(
        self,
        mock_bytes_io,
        mock_table_style,
        mock_table,
        mock_canvas,
        mock_get_stats,
    ):
        """Test that the command executes without errors."""
        metrics_stats = ProjectHealthStatsNode(
            projects_count_healthy=10,
            projects_count_unhealthy=5,
            projects_count_need_attention=3,
            average_score=75.0,
            total_contributors=150,
            total_forks=200,
            total_stars=300,
            projects_percentage_healthy=66.67,
            projects_percentage_need_attention=20.00,
            projects_percentage_unhealthy=13.33,
            monthly_overall_scores=[],
            monthly_overall_scores_months=[],
        )
        table_data = [
            ["Metric", "Value"],
            ["Healthy Projects", f"{metrics_stats.projects_count_healthy}"],
            ["Unhealthy Projects", f"{metrics_stats.projects_count_unhealthy}"],
            ["Need Attention Projects", f"{metrics_stats.projects_count_need_attention}"],
            ["Average Score", f"{metrics_stats.average_score:.2f}"],
            ["Total Contributors", f"{metrics_stats.total_contributors:,}"],
            ["Total Forks", f"{metrics_stats.total_forks:,}"],
            ["Total Stars", f"{metrics_stats.total_stars:,}"],
            ["Healthy Projects Percentage", f"%{metrics_stats.projects_percentage_healthy:.2f}"],
            [
                "Need Attention Projects Percentage",
                f"%{metrics_stats.projects_percentage_need_attention:.2f}",
            ],
            [
                "Unhealthy Projects Percentage",
                f"%{metrics_stats.projects_percentage_unhealthy:.2f}",
            ],
        ]
        mock_get_stats.return_value = metrics_stats
        ProjectHealthMetrics.generate_overview_pdf()
        mock_bytes_io.assert_called_once()
        mock_canvas.assert_called_once_with(mock_bytes_io.return_value)
        canvas = mock_canvas.return_value
        mock_table.assert_called_once_with(
            table_data, colWidths="*", style=mock_table_style.return_value
        )
        mock_table_style.assert_called_once()
        mock_table.return_value.wrapOn.assert_called_once_with(canvas, 400, 500)
        mock_table.return_value.drawOn.assert_called_once_with(canvas, 100, 470)
        canvas.showPage.assert_called_once()
        canvas.save.assert_called_once()
