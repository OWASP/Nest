"""PDF generation for OWASP project health metrics."""

from io import BytesIO

from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table, TableStyle

from apps.owasp.api.internal.nodes.project_health_stats import ProjectHealthStatsNode
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


def create_table(data, col_widths="*"):
    """Create a styled table for PDF generation."""
    return Table(
        data,
        colWidths=col_widths,
        style=TableStyle(
            (
                ("BACKGROUND", (0, 0), (-1, 0), "#f2f2f2"),
                ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("BACKGROUND", (0, 1), (-1, -1), "#ffffff"),
                ("GRID", (0, 0), (-1, -1), 1, "#dddddd"),
            )
        ),
    )


def generate_metrics_overview_pdf(metrics_stats: ProjectHealthStatsNode) -> BytesIO:
    """Generate a PDF overview of project health metrics.

    Args:
        metrics_stats: The project health stats node.

    Returns:
        BytesIO: PDF content as bytes.

    """
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

    table = create_table(table_data)
    table.wrapOn(canvas, 400, 500)
    table.drawOn(canvas, 100, 470)
    canvas.drawCentredString(
        300, 100, f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    canvas.showPage()
    canvas.save()
    buffer.seek(0)
    return buffer


def generate_latest_metrics_pdf(metrics: ProjectHealthMetrics) -> BytesIO | None:
    """Generate a PDF report of the latest health metrics for a project.

    Args:
        metrics (ProjectHealthMetrics): The project health metrics.

    Returns:
        BytesIO: A buffer containing the generated PDF report.

    """
    if not metrics:
        return None

    buffer = BytesIO()
    pdf = Canvas(buffer, pagesize=letter)
    pdf.setTitle(f"Health Metrics Report for {metrics.project.name}")
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(300, 700, f"Health Metrics Report for {metrics.project.name}")
    pdf.drawCentredString(
        300, 680, f"Health Score: {metrics.score:.2f}" if metrics.score is not None else "N/A"
    )
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
    table = create_table(table_data)
    table.wrapOn(pdf, 500, 250)
    table.drawOn(pdf, 50, 220)
    pdf.drawCentredString(
        300, 100, f"Report Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return buffer
