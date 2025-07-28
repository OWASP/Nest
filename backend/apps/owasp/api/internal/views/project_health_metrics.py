"""Views for OWASP project health metrics."""

from django.http import FileResponse, HttpResponseNotFound
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


@require_GET
def generate_project_health_metrics_pdf(_request, project_key: str):
    """Generate and return a PDF report of project health metrics."""
    pdf = ProjectHealthMetrics.generate_latest_metrics_pdf(project_key)
    if not pdf:
        return HttpResponseNotFound(f"No health metrics found for project with key: {project_key}")
    return FileResponse(
        pdf, as_attachment=True, filename=f"{project_key}_health_metrics_report.pdf"
    )
