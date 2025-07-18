"""A command to generate a PDF report of health metrics for an OWASP project."""

from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


class Command(BaseCommand):
    """Generate a PDF report of project health metrics."""

    help = "Generate a PDF report of project health metrics for an OWASP project."

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--project-key", type=str, help="The key of the OWASP project to generate metrics for."
        )

    def handle(self, *args, **options):
        project_key = options["project_key"]
        metrics = (
            ProjectHealthMetrics.get_latest_health_metrics()
            .filter(project__key=f"www-project-{project_key}")
            .first()
        )

        if not metrics:
            self.stdout.write(
                self.style.ERROR(f"No health metrics found for project '{project_key}'")
            )
            return

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setTitle(f"Health Metrics Report for {metrics.project.name}")
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(300, 700, f"Health Metrics Report for {metrics.project.name}")
        pdf.drawCentredString(300, 680, f"Health Score: {metrics.score:.2f}")
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
            ["Has funding issues", "No" if metrics.is_funding_requirements_compliant else "Yes"],
            [
                "Has leadership issues",
                "No" if metrics.is_leader_requirements_compliant else "Yes",
            ],
        ]
        table = Table(table_data, colWidths="*")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), "lightgrey"),
                    ("TEXTCOLOR", (0, 0), (-1, 0), "black"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
                    ("BACKGROUND", (0, 1), (-1, -1), "white"),
                ]
            )
        )
        table.wrapOn(pdf, 500, 300)
        table.drawOn(pdf, 50, 280)
        pdf.drawCentredString(
            300, 100, f"Report Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        pdf.showPage()
        pdf.save()

        pdf_path = Path(settings.BASE_DIR) / "reports" / f"{project_key}_health_metrics_report.pdf"

        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.write_bytes(buffer.getvalue())
        buffer.close()
        self.stdout.write(
            self.style.SUCCESS(f"Health metrics PDF report for {metrics.project.name} generated.")
        )
