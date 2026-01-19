from unittest.mock import MagicMock

from apps.common.middlewares.rate_limit_headers import RateLimitHeadersMiddleware


class DictLikeResponse(dict):
    """A dict-like response object for testing that supports both dict and attribute access."""


class TestRateLimitHeadersMiddleware:
    """Tests for the RateLimitHeadersMiddleware class."""

    def test_adds_headers_when_rate_limit_info_present(self):
        """Test that headers are added when rate_limit_info is present on request."""
        response = DictLikeResponse()
        get_response = MagicMock(return_value=response)

        middleware = RateLimitHeadersMiddleware(get_response)

        mock_request = MagicMock()
        mock_request.rate_limit_info = {
            "limit": 10,
            "remaining": 5,
            "reset": 1234567890,
        }

        result = middleware(mock_request)

        assert response["X-RateLimit-Limit"] == 10
        assert response["X-RateLimit-Remaining"] == 5
        assert response["X-RateLimit-Reset"] == 1234567890
        assert result is response

    def test_no_headers_when_rate_limit_info_absent(self):
        """Test that no headers are added when rate_limit_info is not present."""
        response = DictLikeResponse()
        get_response = MagicMock(return_value=response)

        middleware = RateLimitHeadersMiddleware(get_response)

        # Create a simple object without rate_limit_info attribute
        class SimpleRequest:
            pass

        mock_request = SimpleRequest()

        result = middleware(mock_request)

        # Should not have set any rate limit headers
        assert "X-RateLimit-Limit" not in response
        assert "X-RateLimit-Remaining" not in response
        assert "X-RateLimit-Reset" not in response
        assert result is response

    def test_calls_get_response(self):
        """Test that middleware calls get_response with the request."""

        class SimpleRequest:
            pass

        mock_request = SimpleRequest()
        response = DictLikeResponse()
        get_response = MagicMock(return_value=response)
        middleware = RateLimitHeadersMiddleware(get_response)

        middleware(mock_request)

        get_response.assert_called_once_with(mock_request)

    def test_handles_zero_remaining(self):
        """Test that middleware handles zero remaining correctly."""
        response = DictLikeResponse()
        get_response = MagicMock(return_value=response)

        middleware = RateLimitHeadersMiddleware(get_response)

        mock_request = MagicMock()
        mock_request.rate_limit_info = {
            "limit": 10,
            "remaining": 0,
            "reset": 1234567890,
        }

        middleware(mock_request)

        assert response["X-RateLimit-Remaining"] == 0
