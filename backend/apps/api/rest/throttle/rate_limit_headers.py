"""Custom throttle class that exposes rate limit metadata via request attributes."""

from ninja.throttling import AuthRateThrottle


class RateLimitHeadersThrottle(AuthRateThrottle):
    """AuthRateThrottle that exposes rate limit metadata for response headers.

    This throttle extends AuthRateThrottle to attach rate limit information
    to the request object, which can then be used by middleware to add
    standard rate limit headers to responses:
        - X-RateLimit-Limit: Maximum requests allowed in the current window
        - X-RateLimit-Remaining: Remaining requests in the current window
        - X-RateLimit-Reset: UNIX timestamp when the rate limit resets
    """

    def allow_request(self, request):
        """Check if request should be allowed and attach rate limit metadata.

        Args:
            request: The incoming HTTP request.

        Returns:
            bool: True if the request is allowed, False if throttled.

        """
        result = super().allow_request(request)

        # Calculate rate limit metadata
        if self.history:
            # Reset time is when the oldest request in history expires
            reset_time = int(self.history[-1] + self.duration)
        else:
            # No history, reset is duration from now
            reset_time = int(self.now + self.duration)

        # Attach rate limit info to request for middleware consumption
        request.rate_limit_info = {
            "limit": self.num_requests,
            "remaining": max(0, self.num_requests - len(self.history)),
            "reset": reset_time,
        }

        return result
