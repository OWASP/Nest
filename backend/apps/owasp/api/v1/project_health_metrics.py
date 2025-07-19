"""API endpoint for OWASP project health metrics."""

from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.http import FileResponse
from ninja import Router
from ninja.errors import HttpError

router = Router()


@router.get("/overview-pdf")
def generate_overview_pdf(request):
    """Generate a PDF overview of OWASP project health metrics."""
    call_command("owasp_generate_project_health_metrics_overview_pdf")
    pdf_path = Path(settings.BASE_DIR) / "reports" / "owasp_project_health_metrics_overview.pdf"
    if not pdf_path.exists():
        raise HttpError(404, "PDF file not found")
    return FileResponse(
        Path.open(pdf_path, "rb"),
        as_attachment=True,
        filename="owasp_project_health_metrics_overview.pdf",
    )
