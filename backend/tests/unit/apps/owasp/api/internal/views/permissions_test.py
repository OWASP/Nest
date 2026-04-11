from http import HTTPStatus

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

from apps.owasp.api.internal.views.permissions import (
    dashboard_access_required,
    has_dashboard_permission,
)


class TestPermissions:
    @pytest.fixture
    def user_with_staff(self, mocker):
        user = mocker.Mock()
        user.is_authenticated = True
        user.github_user.is_owasp_staff = True
        return user

    @pytest.fixture
    def user_without_staff(self, mocker):
        user = mocker.Mock()
        user.is_authenticated = True
        user.github_user.is_owasp_staff = False
        return user

    def test_has_dashboard_permission_e2e(self, mocker):
        request = mocker.Mock()
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_E2E_ENVIRONMENT",
            new=True,
        )
        assert has_dashboard_permission(request)

    def test_has_dashboard_permission_staff(self, mocker, user_with_staff):
        request = mocker.Mock()
        request.user = user_with_staff
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_E2E_ENVIRONMENT",
            new=False,
        )
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_FUZZ_ENVIRONMENT",
            new=False,
        )
        assert has_dashboard_permission(request)

    def test_has_dashboard_permission_no_staff(self, mocker, user_without_staff):
        request = mocker.Mock()
        request.user = user_without_staff
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_E2E_ENVIRONMENT",
            new=False,
        )
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_FUZZ_ENVIRONMENT",
            new=False,
        )
        assert not has_dashboard_permission(request)

    def test_has_dashboard_permission_anonymous(self, mocker):
        request = mocker.Mock()
        request.user = AnonymousUser()
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_E2E_ENVIRONMENT",
            new=False,
        )
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_FUZZ_ENVIRONMENT",
            new=False,
        )
        assert not has_dashboard_permission(request)

    def test_dashboard_access_required_decorator_allow(self, mocker, user_with_staff):
        @dashboard_access_required
        def my_view(_request):
            return HttpResponse("OK")

        request = mocker.Mock()
        request.user = user_with_staff
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_E2E_ENVIRONMENT",
            new=False,
        )
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_FUZZ_ENVIRONMENT",
            new=False,
        )

        response = my_view(request)
        assert response.status_code == HTTPStatus.OK
        assert response.content == b"OK"

    def test_dashboard_access_required_decorator_deny(self, mocker, user_without_staff):
        @dashboard_access_required
        def my_view(_request):
            return HttpResponse("OK")

        request = mocker.Mock()
        request.user = user_without_staff
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_E2E_ENVIRONMENT",
            new=False,
        )
        mocker.patch(
            "apps.owasp.api.internal.views.permissions.settings.IS_FUZZ_ENVIRONMENT",
            new=False,
        )

        response = my_view(request)
        assert response.status_code == HTTPStatus.FORBIDDEN
