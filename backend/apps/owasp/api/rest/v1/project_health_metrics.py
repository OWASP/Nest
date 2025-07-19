"""API endpoint for OWASP project health metrics."""

from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.http import FileResponse
from ninja import Router
from ninja.errors import HttpError

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

router = Router()


@router.get("/{project_key}/pdf")
def get_project_health_metrics_pdf(request, project_key: str):
    """Generate and return a PDF report of project health metrics."""
    if not ProjectHealthMetrics.objects.filter(project__key=f"www-project-{project_key}").exists():
        raise HttpError(404, f"No health metrics found for project '{project_key}'")

    file_name = f"{project_key}_health_metrics_report.pdf"
    pdf_path = Path(settings.BASE_DIR) / "reports" / file_name
    call_command(
        "owasp_generate_project_health_metrics_pdf",
        project_key=project_key,
    )
    if not pdf_path.exists():
        raise HttpError(404, f"PDF report for project '{project_key}' not found")
    return FileResponse(Path.open(pdf_path, "rb"), as_attachment=True, filename=file_name)
