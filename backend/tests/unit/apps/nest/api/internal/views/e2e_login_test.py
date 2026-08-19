import json
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from django.http import Http404
from django.test import RequestFactory

from apps.nest.api.internal.views.e2e_login import e2e_login
from apps.nest.models import User


def _post(body: dict | str):
    data = body if isinstance(body, str) else json.dumps(body)
    return RequestFactory().post(
        "/e2e/login/",
        data=data,
        content_type="application/json",
    )


class TestE2ELoginView:
    def test_returns_404_outside_e2e(self):
        with (
            patch(
                "apps.nest.api.internal.views.e2e_login.settings.IS_E2E_ENVIRONMENT",
                False,
            ),
            pytest.raises(Http404),
        ):
            e2e_login(_post({"username": "e2e-mentor"}))

    def test_returns_400_for_invalid_json(self):
        with patch(
            "apps.nest.api.internal.views.e2e_login.settings.IS_E2E_ENVIRONMENT",
            True,
        ):
            response = e2e_login(_post("{"))

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert json.loads(response.content)["ok"] is False

    def test_returns_400_without_username(self):
        with patch(
            "apps.nest.api.internal.views.e2e_login.settings.IS_E2E_ENVIRONMENT",
            True,
        ):
            response = e2e_login(_post({}))

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert json.loads(response.content)["ok"] is False

    def test_returns_404_for_unknown_user(self):
        with (
            patch(
                "apps.nest.api.internal.views.e2e_login.settings.IS_E2E_ENVIRONMENT",
                True,
            ),
            patch(
                "apps.nest.api.internal.views.e2e_login.User.objects.get",
                side_effect=User.DoesNotExist,
            ),
            pytest.raises(Http404),
        ):
            e2e_login(_post({"username": "missing"}))

    def test_logs_in_user(self):
        user = MagicMock()
        request = _post({"username": "e2e-mentor"})

        with (
            patch(
                "apps.nest.api.internal.views.e2e_login.settings.IS_E2E_ENVIRONMENT",
                True,
            ),
            patch(
                "apps.nest.api.internal.views.e2e_login.User.objects.get",
                return_value=user,
            ) as mock_get,
            patch("apps.nest.api.internal.views.e2e_login.login") as mock_login,
        ):
            response = e2e_login(request)

        mock_get.assert_called_once_with(username="e2e-mentor")
        mock_login.assert_called_once_with(request, user)
        assert response.status_code == HTTPStatus.OK
        assert json.loads(response.content) == {"ok": True, "username": "e2e-mentor"}
