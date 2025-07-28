"""Views for OWASP project health metrics."""

from django.http import FileResponse

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


def generate_overview_pdf(_request):
    """Generate a PDF overview of OWASP project health metrics."""
    pdf = ProjectHealthMetrics.generate_overview_pdf()
    return FileResponse(
        pdf,
        as_attachment=True,
        filename="owasp_project_health_metrics_overview.pdf",
    )
