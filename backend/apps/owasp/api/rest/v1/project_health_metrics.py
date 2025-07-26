"""API endpoint for OWASP project health metrics."""

from django.http import FileResponse
from ninja import Router
from ninja.errors import HttpError

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

router = Router()


@router.get("/{project_key}/pdf")
def get_project_health_metrics_pdf(request, project_key: str):
    """Generate and return a PDF report of project health metrics."""
    pdf = ProjectHealthMetrics.generate_latest_metrics_pdf(project_key)
    if not pdf:
        raise HttpError(404, f"Project '{project_key}' not found or has no health metrics")
    return FileResponse(
        pdf, as_attachment=True, filename=f"{project_key}_health_metrics_report.pdf"
    )
