"""Views for OWASP project health metrics."""

from django.http import FileResponse, Http404
from django.views.decorators.http import require_GET

from apps.owasp.api.internal.views.permissions import dashboard_access_required
from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.utils.pdf import generate_latest_metrics_pdf, generate_metrics_overview_pdf


@dashboard_access_required
@require_GET
def generate_overview_pdf(request):  # noqa: ARG001
    """Generate a PDF overview of OWASP project health metrics."""
    return FileResponse(
        generate_metrics_overview_pdf(ProjectHealthMetrics.get_stats()),
        as_attachment=True,
        filename="owasp_project_health_metrics_overview.pdf",
    )


@dashboard_access_required
@require_GET
def generate_project_health_metrics_pdf(request, project_key: str):  # noqa: ARG001
    """Generate and return a PDF report of project health metrics."""
    if not (project := Project.objects.filter(key=f"www-project-{project_key}").first()):
        raise Http404

    if pdf := generate_latest_metrics_pdf(
        ProjectHealthMetrics.get_latest_health_metrics().filter(project=project).first()
    ):
        return FileResponse(
            pdf,
            as_attachment=True,
            filename=f"{project_key}_health_metrics_report.pdf",
        )

    raise Http404
