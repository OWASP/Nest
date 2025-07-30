"""PDF generation for OWASP project health metrics."""

from io import BytesIO

from django.utils import timezone
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table, TableStyle

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


def generate_metrics_overview_pdf() -> BytesIO:
    """Generate a PDF overview of project health metrics.

    Returns:
        BytesIO: PDF content as bytes.

    """
    metrics_stats = ProjectHealthMetrics.get_stats()

    buffer = BytesIO()
    canvas = Canvas(buffer)
    canvas.setFont("Helvetica", 12)
    canvas.setTitle("OWASP Project Health Metrics Overview")
    canvas.drawCentredString(300, 800, "OWASP Project Health Metrics Overview")

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

    table = Table(
        table_data,
        colWidths="*",
        style=TableStyle(
            (
                ("BACKGROUND", (0, 0), (-1, 0), "lightgrey"),
                ("TEXTCOLOR", (0, 0), (-1, 0), "black"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
                ("BACKGROUND", (0, 1), (-1, -1), "white"),
            )
        ),
    )
    table.wrapOn(canvas, 400, 600)
    table.drawOn(canvas, 100, 570)
    canvas.drawCentredString(
        300, 100, f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    canvas.showPage()
    canvas.save()
    buffer.seek(0)
    return buffer
