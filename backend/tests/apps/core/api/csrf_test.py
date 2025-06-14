import json
from http import HTTPStatus

import pytest
from django.contrib.sessions.backends.cache import SessionStore
from django.test import RequestFactory

from apps.core.api.csrf import get_csrf_token


class TestGetCSRFTokenView:
    @pytest.fixture(autouse=True)
    def setup_client(self):
        self.factory = RequestFactory()

    def _make_request_with_session(self, path="/", method="get"):
        request = self.factory.post(path) if method.lower() == "post" else self.factory.get(path)

        request.session = SessionStore()
        request.session.create()

        return request

    def _assert_valid_csrf_response(self, response):
        assert response.status_code == HTTPStatus.OK
        assert response["Content-Type"] == "application/json"

        data = json.loads(response.content)
        assert "csrftoken" in data
        assert isinstance(data["csrftoken"], str)
        assert len(data["csrftoken"]) > 0

    def test_get_csrf_token_success(self):
        request = self._make_request_with_session()
        response = get_csrf_token(request)

        self._assert_valid_csrf_response(response)

    def test_get_csrf_token_returns_json(self):
        request = self._make_request_with_session()
        response = get_csrf_token(request)

        data = json.loads(response.content)
        assert isinstance(data, dict)
        assert len(data) == 1  # Should only contain csrftoken key
        assert "csrftoken" in data

    def test_get_csrf_token_different_requests(self):
        request1 = self._make_request_with_session()
        request2 = self._make_request_with_session()

        response1 = get_csrf_token(request1)
        response2 = get_csrf_token(request2)

        self._assert_valid_csrf_response(response1)
        self._assert_valid_csrf_response(response2)

        data1 = json.loads(response1.content)
        data2 = json.loads(response2.content)

        # Different sessions should have different tokens
        assert data1["csrftoken"] != data2["csrftoken"]

    def test_get_csrf_token_response_structure(self):
        request = self._make_request_with_session()
        response = get_csrf_token(request)

        assert response["Content-Type"] == "application/json"

        data = json.loads(response.content)
        assert isinstance(data, dict)
        assert "csrftoken" in data
        assert len(data["csrftoken"]) > 0

    def test_get_csrf_token_no_session(self):
        request = self.factory.get("/")

        response = get_csrf_token(request)
        self._assert_valid_csrf_response(response)

    def test_get_csrf_token_json_response_format(self):
        request = self._make_request_with_session()
        response = get_csrf_token(request)

        assert hasattr(response, "content")
        assert response["Content-Type"] == "application/json"

        data = json.loads(response.content)
        assert isinstance(data, dict)

        assert list(data.keys()) == ["csrftoken"]
        assert isinstance(data["csrftoken"], str)
        assert data["csrftoken"] != ""
