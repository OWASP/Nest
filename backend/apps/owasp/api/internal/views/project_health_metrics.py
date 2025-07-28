"""Views for OWASP project health metrics."""

from django.http import FileResponse
from django.views.decorators.http import require_GET

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


@require_GET
def generate_overview_pdf(_request):
    """Generate a PDF overview of OWASP project health metrics."""
    pdf = ProjectHealthMetrics.generate_overview_pdf()
    return FileResponse(
        pdf,
        as_attachment=True,
        filename="owasp_project_health_metrics_overview.pdf",
    )
