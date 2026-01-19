from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.throttle.rate_limit_headers import RateLimitHeadersThrottle


class TestRateLimitHeadersThrottle:
    """Tests for the RateLimitHeadersThrottle class."""

    @pytest.fixture
    def throttle(self):
        """Create a RateLimitHeadersThrottle instance with 10/s rate."""
        return RateLimitHeadersThrottle("10/s")

    @pytest.fixture
    def mock_request(self):
        """Create a mock request object."""
        request = MagicMock()
        request.auth = None
        request.META = {"REMOTE_ADDR": "127.0.0.1"}
        return request

    def test_allow_request_attaches_rate_limit_info(self, throttle, mock_request):
        """Test that allow_request attaches rate_limit_info to request."""
        with patch.object(throttle, "cache") as mock_cache, patch.object(
            throttle, "timer", return_value=1000.0
        ):
            mock_cache.get.return_value = []

            result = throttle.allow_request(mock_request)

            assert result is True
            assert hasattr(mock_request, "rate_limit_info")
            assert "limit" in mock_request.rate_limit_info
            assert "remaining" in mock_request.rate_limit_info
            assert "reset" in mock_request.rate_limit_info

    def test_rate_limit_info_has_correct_limit(self, throttle, mock_request):
        """Test that rate_limit_info contains correct limit value."""
        with patch.object(throttle, "cache") as mock_cache, patch.object(
            throttle, "timer", return_value=1000.0
        ):
            mock_cache.get.return_value = []

            throttle.allow_request(mock_request)

            assert mock_request.rate_limit_info["limit"] == 10

    def test_rate_limit_info_remaining_decreases_with_history(self, throttle, mock_request):
        """Test that remaining count decreases as history grows."""
        with patch.object(throttle, "cache") as mock_cache, patch.object(
            throttle, "timer", return_value=1000.0
        ):
            # Simulate 3 previous requests within the window
            mock_cache.get.return_value = [999.9, 999.8, 999.7]

            throttle.allow_request(mock_request)

            # 10 limit - 4 history (including this request) = 6 remaining
            # But since we measure AFTER allow_request adds to history,
            # remaining = 10 - len(history) which is 10 - 4 = 6
            assert mock_request.rate_limit_info["remaining"] == 6

    def test_rate_limit_info_remaining_never_negative(self, throttle, mock_request):
        """Test that remaining count is never negative."""
        with patch.object(throttle, "cache") as mock_cache, patch.object(
            throttle, "timer", return_value=1000.0
        ):
            # Simulate 15 requests (more than limit)
            mock_cache.get.return_value = [999.9 - i * 0.01 for i in range(15)]

            throttle.allow_request(mock_request)

            assert mock_request.rate_limit_info["remaining"] >= 0

    def test_rate_limit_info_reset_is_integer_timestamp(self, throttle, mock_request):
        """Test that reset is an integer UNIX timestamp."""
        with patch.object(throttle, "cache") as mock_cache, patch.object(
            throttle, "timer", return_value=1000.0
        ):
            mock_cache.get.return_value = []

            throttle.allow_request(mock_request)

            assert isinstance(mock_request.rate_limit_info["reset"], int)

    def test_throttle_returns_false_when_limit_exceeded(self, throttle, mock_request):
        """Test that throttle returns False when rate limit is exceeded."""
        with patch.object(throttle, "cache") as mock_cache, patch.object(
            throttle, "timer", return_value=1000.0
        ):
            # Simulate 10 requests within the 1-second window
            mock_cache.get.return_value = [999.9 - i * 0.01 for i in range(10)]

            result = throttle.allow_request(mock_request)

            assert result is False
            # Should still have rate_limit_info attached
            assert hasattr(mock_request, "rate_limit_info")
