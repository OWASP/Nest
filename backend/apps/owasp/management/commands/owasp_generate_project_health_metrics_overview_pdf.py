"""A command to generate a PDF overview of OWASP project health metrics."""

from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.tables import Table, TableStyle

import settings.base
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


class Command(BaseCommand):
    help = "Generate a PDF overview of OWASP project health metrics."

    def handle(self, *args, **options):
        metrics_stats = ProjectHealthMetrics.get_stats()

        buffer = BytesIO()
        canvas = Canvas(buffer)
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
        canvas.drawCentredString(
            300, 100, f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        canvas.showPage()
        canvas.save()
        pdf_path = (
            Path(settings.base.Base.BASE_DIR)
            / "reports"
            / "owasp_project_health_metrics_overview.pdf"
        )
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.write_bytes(buffer.getvalue())
        buffer.close()
        self.stdout.write(self.style.SUCCESS("PDF overview generated successfully."))
