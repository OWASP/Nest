"""Views for OWASP project health metrics."""

from django.http import FileResponse
from django.views.decorators.http import require_GET

from apps.owasp.utils.pdf import generate_metrics_overview_pdf


@require_GET
def generate_overview_pdf(_request):
    """Generate a PDF overview of OWASP project health metrics."""
    return FileResponse(
        generate_metrics_overview_pdf(),
        as_attachment=True,
        filename="owasp_project_health_metrics_overview.pdf",
    )
