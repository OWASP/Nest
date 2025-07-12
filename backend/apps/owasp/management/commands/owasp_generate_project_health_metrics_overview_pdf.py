"""A command to generate a PDF overview of OWASP project health metrics."""

from django.core.management.base import BaseCommand
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.tables import Table, TableStyle

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


class Command(BaseCommand):
    help = "Generate a PDF overview of OWASP project health metrics."

    def handle(self, *args, **options):
        metrics_stats = ProjectHealthMetrics.get_stats()

        pdf_file_path = "owasp_project_metrics_overview.pdf"
        canvas = Canvas(pdf_file_path)
        canvas.setFont("Helvetica", 12)
        canvas.setTitle("OWASP Project Health Metrics Overview")
        canvas.drawCentredString(300, 800, "OWASP Project Health Metrics Overview")
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
        table.wrapOn(canvas, 400, 600)
        table.drawOn(canvas, 100, 570)
        canvas.save()
        self.stdout.write(self.style.SUCCESS(f"PDF overview generated at {pdf_file_path}"))
