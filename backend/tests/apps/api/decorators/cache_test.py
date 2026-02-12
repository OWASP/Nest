"""Test cases for the API cache decorator."""

from http import HTTPStatus
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse

import pytest
from django.http import HttpRequest, HttpResponse

from apps.api.decorators.cache import cache_response, generate_key


@pytest.mark.parametrize(
    ("full_path", "prefix", "expected_key"),
    [
        ("/api/test", "p1", "p1:/api/test"),
        ("/api/test?a=1", "p2", "p2:/api/test?a=1"),
        ("/api/test?a=1&b=2", "p3", "p3:/api/test?a=1&b=2"),
        ("/api/test?b=2&a=1", "p4", "p4:/api/test?b=2&a=1"),
    ],
)
def test_generate_cache_key(full_path, prefix, expected_key):
    """Test cases for the generate cache key function."""
    request = HttpRequest()
    parsed_url = urlparse(full_path)
    request.path = parsed_url.path
    request.META["QUERY_STRING"] = parsed_url.query

    assert generate_key(request, prefix) == expected_key


class TestCacheResponse:
    """Test cases for the cache response decorator."""

    @pytest.fixture
    def mock_request(self):
        """Return a mock GET request."""
        request = HttpRequest()
        request.method = "GET"
        request.path = "/api/test"
        request.GET = {}
        return request

    @patch("apps.api.decorators.cache.cache")
    def test_get_request_caches_response(self, mock_cache, mock_request):
        """Test that a GET request caches the response."""
        mock_cache.get.return_value = None
        view_func = MagicMock(return_value=HttpResponse(status=HTTPStatus.OK))
        decorated_view = cache_response(ttl=60)(view_func)

        response = decorated_view(mock_request)

        assert response.status_code == HTTPStatus.OK
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
        view_func.assert_called_once_with(mock_request)

    @patch("apps.api.decorators.cache.cache")
    def test_get_request_returns_cached_response(self, mock_cache, mock_request):
        """Test that a GET request returns a cached response if available."""
        cached_response = HttpResponse(status=HTTPStatus.OK, content=b"cached")
        mock_cache.get.return_value = cached_response
        view_func = MagicMock()
        decorated_view = cache_response(ttl=60)(view_func)

        response = decorated_view(mock_request)

        assert response == cached_response
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called()
        view_func.assert_not_called()

    @pytest.mark.parametrize("method", ["POST", "PUT", "DELETE"])
    @patch("apps.api.decorators.cache.cache")
    def test_non_get_head_requests_not_cached(self, mock_cache, method, mock_request):
        """Test that non-GET/HEAD requests are not cached."""
        mock_request.method = method
        view_func = MagicMock(return_value=HttpResponse())
        decorated_view = cache_response(ttl=60)(view_func)

        decorated_view(mock_request)

        mock_cache.get.assert_not_called()
        mock_cache.set.assert_not_called()
        view_func.assert_called_once_with(mock_request)

    @pytest.mark.parametrize(
        "status_code",
        [
            HTTPStatus.CREATED,
            HTTPStatus.NO_CONTENT,
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.NOT_FOUND,
            HTTPStatus.INTERNAL_SERVER_ERROR,
        ],
    )
    @patch("apps.api.decorators.cache.cache")
    def test_non_200_responses_not_cached(self, mock_cache, status_code, mock_request):
        """Test that responses with non-200 status codes are not cached."""
        mock_cache.get.return_value = None
        view_func = MagicMock(return_value=HttpResponse(status=status_code))
        decorated_view = cache_response(ttl=60)(view_func)

        response = decorated_view(mock_request)

        assert response.status_code == status_code
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called()
        view_func.assert_called_once_with(mock_request)

    @patch("apps.api.decorators.cache.cache")
    def test_head_request_caches_response(self, mock_cache, mock_request):
        """Test that a HEAD request caches the response."""
        mock_request.method = "HEAD"
        mock_cache.get.return_value = None
        view_func = MagicMock(return_value=HttpResponse(status=HTTPStatus.OK))
        decorated_view = cache_response(ttl=60)(view_func)

        response = decorated_view(mock_request)

        assert response.status_code == HTTPStatus.OK
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()

    @patch("apps.api.decorators.cache.settings")
    @patch("apps.api.decorators.cache.cache")
    def test_cache_response_with_default_ttl_and_prefix(
        self, mock_cache, mock_settings, mock_request
    ):
        """Test cache_response uses default TTL and prefix from settings."""
        mock_settings.API_CACHE_TIME_SECONDS = 300
        mock_settings.API_CACHE_PREFIX = "test_prefix"
        mock_cache.get.return_value = None
        view_func = MagicMock(return_value=HttpResponse(status=HTTPStatus.OK))

        decorated_view = cache_response()(view_func)

        response = decorated_view(mock_request)

        assert response.status_code == HTTPStatus.OK
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()

    @patch("apps.api.decorators.cache.cache")
    def test_cache_response_with_custom_prefix(self, mock_cache, mock_request):
        """Test cache_response with custom prefix."""
        mock_cache.get.return_value = None
        view_func = MagicMock(return_value=HttpResponse(status=HTTPStatus.OK))
        decorated_view = cache_response(ttl=60, prefix="custom_prefix")(view_func)

        response = decorated_view(mock_request)

        assert response.status_code == HTTPStatus.OK

        cache_key_call = mock_cache.get.call_args[0][0]
        assert cache_key_call.startswith("custom_prefix:")
        mock_cache.set.assert_called_once()
