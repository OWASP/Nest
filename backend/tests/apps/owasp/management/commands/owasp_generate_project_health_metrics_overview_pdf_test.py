from unittest.mock import patch

from django.core.management import call_command

from apps.owasp.graphql.nodes.project_health_stats import ProjectHealthStatsNode


class TestOwaspGenerateProjectHealthMetricsOverviewPdf:
    @patch("apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_stats")
    @patch("reportlab.pdfgen.canvas.Canvas")
    @patch("reportlab.platypus.tables.Table")
    @patch("reportlab.platypus.tables.TableStyle")
    @patch("io.BytesIO")
    @patch("pathlib.Path")
    def test_command_execution(
        self, mock_path, mock_bytes_io, mock_table_style, mock_table, mock_canvas, mock_get_stats
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
        )
        table_data = [
            ["Metric", "Value"],
            ["Healthy Projects", f"{metrics_stats.projects_count_healthy}"],
            ["Unhealthy Projects", f"{metrics_stats.projects_count_unhealthy}"],
            ["Projects Needing Attention", f"{metrics_stats.projects_count_need_attention}"],
            ["Average Score", f"{metrics_stats.average_score:.2f}"],
            ["Total Contributors", f"{metrics_stats.total_contributors:,}"],
            ["Total Forks", f"{metrics_stats.total_forks:,}"],
            ["Total Stars", f"{metrics_stats.total_stars:,}"],
            ["Healthy Projects Percentage", f"%{metrics_stats.projects_percentage_healthy:.2f}"],
            [
                "Projects Needing Attention Percentage",
                f"%{metrics_stats.projects_percentage_need_attention:.2f}",
            ],
            [
                "Unhealthy Projects Percentage",
                f"%{metrics_stats.projects_percentage_unhealthy:.2f}",
            ],
        ]
        mock_get_stats.return_value = metrics_stats
        call_command("owasp_generate_project_health_metrics_overview_pdf")
        canvas = mock_canvas.return_value
        mock_table.assert_called_once_with(table_data, colWidths="*")
        mock_table_style.assert_called_once()
        mock_table.return_value.wrapOn.assert_called_once_with(canvas, 400, 600)
        mock_table.return_value.drawOn.assert_called_once_with(canvas, 100, 570)
        canvas.showPage.assert_called_once()
        canvas.save.assert_called_once()
