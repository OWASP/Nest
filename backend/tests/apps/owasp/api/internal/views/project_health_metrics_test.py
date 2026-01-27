import io

import pytest
from django.http import Http404

from apps.owasp.api.internal.views.project_health_metrics import (
    generate_overview_pdf,
    generate_project_health_metrics_pdf,
)


class TestProjectHealthMetricsViews:
    @pytest.fixture
    def user_with_permission(self, mocker):
        user = mocker.Mock()
        user.is_authenticated = True
        user.github_user.is_owasp_staff = True
        return user

    def test_generate_overview_pdf(self, user_with_permission, mocker):
        mock_stats = mocker.Mock()
        mocker.patch(
            "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_stats",
            return_value=mock_stats,
        )

        mocker.patch(
            "apps.owasp.api.internal.views.project_health_metrics.generate_metrics_overview_pdf",
            return_value=io.BytesIO(b"PDF CONTENT"),
        )

        request = mocker.Mock()
        request.method = "GET"
        request.user = user_with_permission

        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_E2E_ENVIRONMENT",
            new=False,
        )
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_FUZZ_ENVIRONMENT",
            new=False,
        )

        response = generate_overview_pdf(request)

        assert response.status_code == 200
        content = b"".join(response.streaming_content)
        assert b"PDF CONTENT" in content
        assert response["Content-Type"] == "application/pdf"

    def test_generate_project_health_metrics_pdf_success(self, user_with_permission, mocker):
        project_key = "juice-shop"
        mock_project = mocker.Mock()

        mocker.patch(
            "apps.owasp.models.project.Project.objects.filter",
            return_value=mocker.Mock(first=lambda: mock_project),
        )

        mock_qs = mocker.Mock()
        mock_qs.filter.return_value.first.return_value = mocker.Mock()
        mocker.patch(
            "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_latest_health_metrics",
            return_value=mock_qs,
        )

        mocker.patch(
            "apps.owasp.api.internal.views.project_health_metrics.generate_latest_metrics_pdf",
            return_value=io.BytesIO(b"PROJECT PDF"),
        )

        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_E2E_ENVIRONMENT",
            new=False,
        )
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_FUZZ_ENVIRONMENT",
            new=False,
        )

        request = mocker.Mock()
        request.method = "GET"
        request.user = user_with_permission

        response = generate_project_health_metrics_pdf(request, project_key)

        assert response.status_code == 200
        content = b"".join(response.streaming_content)
        assert b"PROJECT PDF" in content
        assert (
            f'filename="{project_key}_health_metrics_report.pdf"'
            in response["Content-Disposition"]
        )

    def test_generate_project_health_metrics_pdf_project_not_found(
        self, user_with_permission, mocker
    ):
        mocker.patch(
            "apps.owasp.models.project.Project.objects.filter",
            return_value=mocker.Mock(first=lambda: None),
        )
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_E2E_ENVIRONMENT",
            new=False,
        )
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_FUZZ_ENVIRONMENT",
            new=False,
        )

        request = mocker.Mock()
        request.method = "GET"
        request.user = user_with_permission

        with pytest.raises(Http404):
            generate_project_health_metrics_pdf(request, "unknown")

    def test_generate_project_health_metrics_pdf_no_metrics(self, user_with_permission, mocker):
        mock_project = mocker.Mock()
        mocker.patch(
            "apps.owasp.models.project.Project.objects.filter",
            return_value=mocker.Mock(first=lambda: mock_project),
        )

        mock_qs = mocker.Mock()
        mock_qs.filter.return_value.first.return_value = mocker.Mock()
        mocker.patch(
            "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.get_latest_health_metrics",
            return_value=mock_qs,
        )

        mocker.patch(
            "apps.owasp.api.internal.views.project_health_metrics.generate_latest_metrics_pdf",
            return_value=None,
        )
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_E2E_ENVIRONMENT",
            new=False,
        )
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_FUZZ_ENVIRONMENT",
            new=False,
        )

        request = mocker.Mock()
        request.method = "GET"
        request.user = user_with_permission

        with pytest.raises(Http404):
            generate_project_health_metrics_pdf(request, "fail")
