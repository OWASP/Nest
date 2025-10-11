"""URLs for OWASP project health metrics."""

from django.urls import path

from apps.owasp.api.internal.views.project_health_metrics import (
    generate_overview_pdf,
    generate_project_health_metrics_pdf,
)

urlpatterns = [
    path(
        "project-health-metrics/overview/pdf/",
        generate_overview_pdf,
        name="project_health_metrics_overview_pdf",
    ),
    path(
        "project-health-metrics/<str:project_key>/pdf/",
        generate_project_health_metrics_pdf,
        name="project_health_metrics_pdf",
    ),
]
