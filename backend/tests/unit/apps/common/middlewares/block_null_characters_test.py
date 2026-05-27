import json
from http import HTTPStatus

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, QueryDict
from django.test import RequestFactory
from django.utils.datastructures import MultiValueDict

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
        assert response.status_code == HTTPStatus.OK
        assert response.content == b"OK"

    def test_null_in_path_blocks(self, middleware, factory):
        request = factory.get("/path/with/\x00/null")
        response = middleware(request)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert json.loads(response.content) == {
            "message": "Request contains null characters in URL, parameters, or form data",
            "errors": {},
        }

    def test_null_in_query_params_blocks(self, middleware, factory):
        request = factory.get("/clean/path", {"q": "bad\x00value"})
        response = middleware(request)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_null_in_post_data_blocks(self, middleware, factory):
        request = factory.post("/clean/path", {"data": "bad\x00value"})
        response = middleware(request)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_null_in_file_field_name_blocks(self, middleware, factory):
        upload = SimpleUploadedFile(
            "payload.bin",
            b"abc",
            content_type="application/octet-stream",
        )
        request = factory.post("/clean/path", data={})
        request._post = QueryDict("")
        request._files = MultiValueDict({"file\x00field": [upload]})
        response = middleware(request)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_null_in_file_name_blocks(self, middleware, factory):
        upload = SimpleUploadedFile(
            "payload.bin",
            b"abc",
            content_type="application/octet-stream",
        )
        upload.name = "payload\x00.bin"
        request = factory.post("/clean/path", data={})
        request._post = QueryDict("")
        request._files = MultiValueDict({"file": [upload]})
        response = middleware(request)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_null_in_file_content_type_blocks(self, middleware, factory):
        request = factory.post(
            "/clean/path",
            data={
                "file": SimpleUploadedFile(
                    "payload.bin",
                    b"abc",
                    content_type="application/\x00octet-stream",
                )
            },
        )
        response = middleware(request)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_null_in_file_content_type_extra_blocks(self, middleware, factory):
        upload = SimpleUploadedFile(
            "payload.bin",
            b"abc",
            content_type="application/octet-stream",
        )
        upload.content_type_extra = {"charset": "utf\x00-8"}
        request = factory.post("/clean/path", data={})
        request._post = QueryDict("")
        request._files = MultiValueDict({"file": [upload]})
        response = middleware(request)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_null_in_body_blocks(self, middleware, factory):
        request = factory.post(
            "/clean/path",
            data=b'{"key": "bad\x00value"}',
            content_type="application/json",
        )
        response = middleware(request)
        assert response.status_code == HTTPStatus.BAD_REQUEST
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
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_multipart_form_data_skips_body_check(self, middleware, factory):
        request = factory.post(
            "/clean/path",
            data={
                "file": SimpleUploadedFile(
                    "payload.bin",
                    b"abc\x00def",
                    content_type="application/octet-stream",
                )
            },
        )
        response = middleware(request)
        assert response.status_code == HTTPStatus.OK

    def test_fake_multipart_content_type_does_not_skip_body_check(self, middleware, factory):
        request = factory.post(
            "/clean/path",
            data=b'{"key": "bad\x00value"}',
            content_type="multipart/form-data-bad",
        )
        response = middleware(request)
        assert response.status_code == HTTPStatus.BAD_REQUEST
