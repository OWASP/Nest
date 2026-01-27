import json

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from apps.common.middlewares.block_null_characters import BlockNullCharactersMiddleware


class TestBlockNullCharactersMiddleware:
    @pytest.fixture
    def middleware(self):
        def get_response(_request):
            return HttpResponse("OK")

        return BlockNullCharactersMiddleware(get_response)

    @pytest.fixture
    def factory(self):
        return RequestFactory()

    def test_clean_request_passes(self, middleware, factory):
        request = factory.get("/clean/path")
        response = middleware(request)
        assert response.status_code == 200
        assert response.content == b"OK"

    def test_null_in_path_blocks(self, middleware, factory):
        request = factory.get("/path/with/\x00/null")
        response = middleware(request)
        assert response.status_code == 400
        assert json.loads(response.content) == {
            "message": "Request contains null characters in URL or parameters "
            "which are not allowed.",
            "errors": {},
        }

    def test_null_in_query_params_blocks(self, middleware, factory):
        request = factory.get("/clean/path", {"q": "bad\x00value"})
        response = middleware(request)
        assert response.status_code == 400

    def test_null_in_post_data_blocks(self, middleware, factory):
        request = factory.post("/clean/path", {"data": "bad\x00value"})
        response = middleware(request)
        assert response.status_code == 400

    def test_null_in_body_blocks(self, middleware, factory):
        request = factory.post(
            "/clean/path",
            data=b'{"key": "bad\x00value"}',
            content_type="application/json",
        )
        response = middleware(request)
        assert response.status_code == 400
        assert json.loads(response.content) == {
            "message": "Request contains null characters in body which are not allowed.",
            "errors": {},
        }

    def test_unicode_null_in_body_blocks(self, middleware, factory):
        request = factory.post(
            "/clean/path",
            data=b'{"key": "bad\\u0000value"}',
            content_type="application/json",
        )
        response = middleware(request)
        assert response.status_code == 400
