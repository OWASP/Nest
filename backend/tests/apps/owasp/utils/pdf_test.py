"""Test cases for  OWASP project health metrics pdf generation."""

from unittest.mock import MagicMock, patch

from reportlab.lib.pagesizes import letter

from apps.owasp.api.internal.nodes.project_health_stats import ProjectHealthStatsNode
from apps.owasp.utils.pdf import generate_latest_metrics_pdf, generate_metrics_overview_pdf


class TestGenerateMetricsPDF:
    @patch("apps.owasp.utils.pdf.ProjectHealthMetrics.get_stats")
    @patch("apps.owasp.utils.pdf.Canvas")
    @patch("apps.owasp.utils.pdf.Table")
    @patch("apps.owasp.utils.pdf.TableStyle")
    @patch("apps.owasp.utils.pdf.BytesIO")
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
        table_data = (
            ("Metric", "Value"),
            ("Healthy Projects", f"{metrics_stats.projects_count_healthy}"),
            ("Unhealthy Projects", f"{metrics_stats.projects_count_unhealthy}"),
            ("Need Attention Projects", f"{metrics_stats.projects_count_need_attention}"),
            (
                "Average Score",
                f"{metrics_stats.average_score:.2f}"
                if metrics_stats.average_score is not None
                else "N/A",
            ),
            ("Total Contributors", f"{metrics_stats.total_contributors:,}"),
            ("Total Forks", f"{metrics_stats.total_forks:,}"),
            ("Total Stars", f"{metrics_stats.total_stars:,}"),
            (
                "Healthy Projects Percentage",
                f"{metrics_stats.projects_percentage_healthy:.2f}%",
            ),
            (
                "Need Attention Projects Percentage",
                f"{metrics_stats.projects_percentage_need_attention:.2f}%",
            ),
            (
                "Unhealthy Projects Percentage",
                f"{metrics_stats.projects_percentage_unhealthy:.2f}%",
            ),
        )
        mock_get_stats.return_value = metrics_stats
        generate_metrics_overview_pdf(metrics_stats)
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

    @patch(
        "apps.owasp.utils.pdf.ProjectHealthMetrics.get_latest_health_metrics",
    )
    @patch("apps.owasp.utils.pdf.Canvas")
    @patch("apps.owasp.utils.pdf.Table")
    @patch("apps.owasp.utils.pdf.TableStyle")
    @patch("apps.owasp.utils.pdf.BytesIO")
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
            age_days_requirement=365,
            contributors_count=20,
            forks_count=15,
            is_funding_requirements_compliant=True,
            is_leader_requirements_compliant=True,
            last_commit_days=5,
            last_commit_days_requirement=7,
            last_pull_request_days=2,
            last_pull_request_days_requirement=30,
            last_release_days=10,
            last_release_days_requirement=14,
            open_issues_count=10,
            open_pull_requests_count=3,
            owasp_page_last_update_days=20,
            owasp_page_last_update_days_requirement=90,
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
        generate_latest_metrics_pdf(metrics)
        mock_bytes_io.assert_called_once()
        mock_canvas.assert_called_once_with(mock_bytes_io.return_value, pagesize=letter)
        canvas = mock_canvas.return_value
        table_data = (
            ("Metric", "Value"),
            ("Project Age", f"{metrics.age_days}/{metrics.age_days_requirement} days"),
            (
                "Last Commit",
                f"{metrics.last_commit_days}/{metrics.last_commit_days_requirement} days",
            ),
            (
                "Last Pull Request",
                # To bypass ruff long line error
                "/".join(
                    [
                        str(metrics.last_pull_request_days),
                        f"{metrics.last_pull_request_days_requirement} days",
                    ]
                ),
            ),
            (
                "Last Release",
                f"{metrics.last_release_days}/{metrics.last_release_days_requirement} days",
            ),
            (
                "OWASP Page Last Update",
                # To bypass ruff long line error
                "/".join(
                    [
                        str(metrics.owasp_page_last_update_days),
                        f"{metrics.owasp_page_last_update_days_requirement} days",
                    ]
                ),
            ),
            ("Open/Total Issues", f"{metrics.open_issues_count}/{metrics.total_issues_count}"),
            (
                "Open/Total Pull Requests",
                f"{metrics.open_pull_requests_count}/{metrics.total_pull_requests_count}",
            ),
            (
                "Recent/Total Releases",
                f"{metrics.recent_releases_count}/{metrics.total_releases_count}",
            ),
            ("Forks", metrics.forks_count),
            ("Stars", metrics.stars_count),
            (
                "Unassigned/Unanswered Issues",
                f"{metrics.unassigned_issues_count}/{metrics.unanswered_issues_count}",
            ),
            ("Contributors", metrics.contributors_count),
            (
                "Has funding policy issues",
                "No" if metrics.is_funding_requirements_compliant else "Yes",
            ),
            (
                "Has leadership policy issues",
                "No" if metrics.is_leader_requirements_compliant else "Yes",
            ),
        )
        mock_table.assert_called_once_with(
            table_data, colWidths="*", style=mock_table_style.return_value
        )
        mock_table_style.assert_called_once()

        mock_table.return_value.wrapOn.assert_called_once_with(canvas, 500, 250)
        mock_table.return_value.drawOn.assert_called_once_with(canvas, 50, 220)
        canvas.showPage.assert_called_once()
        canvas.save.assert_called_once()
