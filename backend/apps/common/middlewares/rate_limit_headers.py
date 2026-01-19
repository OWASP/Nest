"""Middleware to add rate limit headers to API responses."""

from django.http import HttpRequest, HttpResponse


class RateLimitHeadersMiddleware:
    """Middleware to add rate limit metadata headers to responses.

    This middleware reads rate limit information attached to the request
    by RateLimitHeadersThrottle and adds standard headers to the response:
        - X-RateLimit-Limit: Maximum requests allowed in the current window
        - X-RateLimit-Remaining: Remaining requests in the current window
        - X-RateLimit-Reset: UNIX timestamp when the rate limit resets
    """

    def __init__(self, get_response):
        """Initialize the middleware.

        Args:
            get_response: The next middleware or view in the chain.

        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and add rate limit headers to the response.

        Args:
            request: The incoming HTTP request.

        Returns:
            HttpResponse: The response with rate limit headers added if applicable.

        """
        response = self.get_response(request)

        # Check if rate limit info was attached by the throttle
        rate_limit_info = getattr(request, "rate_limit_info", None)
        if rate_limit_info:
            response["X-RateLimit-Limit"] = rate_limit_info["limit"]
            response["X-RateLimit-Remaining"] = rate_limit_info["remaining"]
            response["X-RateLimit-Reset"] = rate_limit_info["reset"]

        return response
