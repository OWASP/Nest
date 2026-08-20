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
        request = _post({"username": "e2e-mentor"})
        with (
            patch(
                "apps.nest.api.internal.views.e2e_login.settings.IS_E2E_ENVIRONMENT",
                new=False,
            ),
            pytest.raises(Http404),
        ):
            e2e_login(request)

    def test_returns_400_for_invalid_json(self):
        request = _post("{")
        with patch(
            "apps.nest.api.internal.views.e2e_login.settings.IS_E2E_ENVIRONMENT",
            new=True,
        ):
            response = e2e_login(request)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert json.loads(response.content)["ok"] is False

    @pytest.mark.parametrize("payload", ["[1, 2]", '"string"', "123", "null"])
    def test_returns_400_for_non_dict_json(self, payload):
        request = _post(payload)
        with patch(
            "apps.nest.api.internal.views.e2e_login.settings.IS_E2E_ENVIRONMENT",
            new=True,
        ):
            response = e2e_login(request)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert json.loads(response.content)["ok"] is False

    @pytest.mark.parametrize("username", [123, True, [], {}, "   "])
    def test_returns_400_for_invalid_username_type(self, username):
        request = _post({"username": username})
        with patch(
            "apps.nest.api.internal.views.e2e_login.settings.IS_E2E_ENVIRONMENT",
            new=True,
        ):
            response = e2e_login(request)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert json.loads(response.content)["ok"] is False

    def test_returns_404_for_non_allowlisted_user(self):
        request = _post({"username": "admin"})
        with (
            patch(
                "apps.nest.api.internal.views.e2e_login.settings.IS_E2E_ENVIRONMENT",
                new=True,
            ),
            pytest.raises(Http404),
        ):
            e2e_login(request)

    def test_returns_404_for_unknown_user(self):
        request = _post({"username": "e2e-mentor"})
        with (
            patch(
                "apps.nest.api.internal.views.e2e_login.settings.IS_E2E_ENVIRONMENT",
                new=True,
            ),
            patch(
                "apps.nest.api.internal.views.e2e_login.User.objects.get",
                side_effect=User.DoesNotExist,
            ),
            pytest.raises(Http404),
        ):
            e2e_login(request)

    def test_logs_in_user(self):
        user = MagicMock()
        request = _post({"username": "e2e-mentor"})

        with (
            patch(
                "apps.nest.api.internal.views.e2e_login.settings.IS_E2E_ENVIRONMENT",
                new=True,
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
