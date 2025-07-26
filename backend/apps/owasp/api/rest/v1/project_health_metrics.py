"""API endpoint for OWASP project health metrics."""

from django.http import FileResponse
from ninja import Router

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

router = Router()


@router.get("/overview-pdf")
def generate_overview_pdf(request):
    """Generate a PDF overview of OWASP project health metrics."""
    pdf = ProjectHealthMetrics.generate_overview_pdf()
    return FileResponse(
        pdf,
        as_attachment=True,
        filename="owasp_project_health_metrics_overview.pdf",
    )
