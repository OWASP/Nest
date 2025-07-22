from unittest.mock import MagicMock, patch

from django.conf import settings
from django.core.management import call_command
from reportlab.lib.pagesizes import letter


class TestOwaspGenerateProjectHealthMetricsPdf:
    @patch(
        "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_latest_health_metrics",
    )
    @patch("reportlab.pdfgen.canvas.Canvas")
    @patch("reportlab.platypus.Table")
    @patch("reportlab.platypus.TableStyle")
    @patch("io.BytesIO")
    @patch("pathlib.Path")
    def test_handle(
        self,
        mock_path,
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
        call_command("owasp_generate_project_health_metrics_pdf", project_key="test")
        mock_bytes_io.assert_called_once()
        mock_canvas.assert_called_once_with(mock_bytes_io.return_value, pagesize=letter)
        canvas = mock_canvas.return_value
        table_data = [
            ["Metric", "Value"],
            ["Project Age (days)", metrics.age_days],
            ["Last Commit (days)", metrics.last_commit_days],
            ["Last Commit Requirement (days)", metrics.last_commit_days_requirement],
            ["Last Pull Request (days)", metrics.last_pull_request_days],
            ["Last Release (days)", metrics.last_release_days],
            ["Last Release Requirement (days)", metrics.last_release_days_requirement],
            ["OWASP Page Last Update (days)", metrics.owasp_page_last_update_days],
            ["Open Issues", metrics.open_issues_count],
            ["Total Issues", metrics.total_issues_count],
            ["Open Pull Requests", metrics.open_pull_requests_count],
            ["Total Pull Requests", metrics.total_pull_requests_count],
            ["Recent Releases", metrics.recent_releases_count],
            ["Total Releases", metrics.total_releases_count],
            ["Forks", metrics.forks_count],
            ["Stars", metrics.stars_count],
            ["Contributors", metrics.contributors_count],
            ["Unassigned Issues", metrics.unassigned_issues_count],
            ["Unanswered Issues", metrics.unanswered_issues_count],
            ["Has funding issues", "No"],
            [
                "Has leadership issues",
                "No",
            ],
        ]
        mock_table.assert_called_once_with(table_data, colWidths="*")
        mock_table_style.assert_called_once()

        mock_table.return_value.wrapOn.assert_called_once_with(canvas, 500, 300)
        mock_table.return_value.drawOn.assert_called_once_with(canvas, 50, 280)
        canvas.showPage.assert_called_once()
        canvas.save.assert_called_once()
        mock_path.assert_called_once_with(settings.BASE_DIR)
        mock_bytes_io.return_value.close.assert_called_once()
