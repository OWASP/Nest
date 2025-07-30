"""Test cases for  OWASP project health metrics pdf generation."""

from unittest.mock import patch

from apps.owasp.api.internal.nodes.project_health_stats import ProjectHealthStatsNode
from apps.owasp.utils.pdf import generate_metrics_overview_pdf


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
        generate_metrics_overview_pdf()
        mock_bytes_io.assert_called_once()
        mock_canvas.assert_called_once_with(mock_bytes_io.return_value)
        canvas = mock_canvas.return_value
        mock_table.assert_called_once_with(
            table_data, colWidths="*", style=mock_table_style.return_value
        )
        mock_table_style.assert_called_once()
        mock_table.return_value.wrapOn.assert_called_once_with(canvas, 400, 600)
        mock_table.return_value.drawOn.assert_called_once_with(canvas, 100, 570)
        canvas.showPage.assert_called_once()
        canvas.save.assert_called_once()
