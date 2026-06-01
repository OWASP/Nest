from django.test import SimpleTestCase, override_settings
from django.urls import resolve, reverse

from apps.owasp.api.internal.views.project_health_metrics import (
    generate_overview_pdf,
    generate_project_health_metrics_pdf,
)


@override_settings(ROOT_URLCONF="apps.owasp.api.internal.views.urls")
class TestOwaspUrls(SimpleTestCase):
    def test_overview_pdf_url(self):
        url = reverse("project_health_metrics_overview_pdf")
        assert url == "/project-health-metrics/overview/pdf/"
        resolver = resolve(url)
        assert resolver.func == generate_overview_pdf

    def test_project_health_metrics_pdf_url(self):
        url = reverse("project_health_metrics_pdf", kwargs={"project_key": "test-project"})
        assert url == "/project-health-metrics/test-project/pdf/"
        resolver = resolve(url)
        assert resolver.func == generate_project_health_metrics_pdf
