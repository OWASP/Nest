"""Set Referer for server-to-server requests that lack it but send a CSRF token.

Node's fetch does not send the Referer header for programmatic requests. When the
frontend (Next.js) calls the GraphQL API from the server, Django's CSRF middleware
rejects the request due to missing Referer. This middleware sets HTTP_REFERER to a
trusted origin when the path is /graphql/, Referer is missing, and X-CSRFToken is
present, so the CSRF middleware's referer check passes. The token check is unchanged.
"""

from django.conf import settings
from django.http import HttpRequest


class CsrfRefererFallbackMiddleware:
    """Set a trusted Referer for API requests that have a token but no Referer."""

    def __init__(self, get_response):
        """Initialize middleware with get_response callable."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """Set HTTP_REFERER when missing for token-bearing requests to /graphql/."""
        if (
            request.path.startswith("/graphql/")
            and not request.META.get("HTTP_REFERER")
            and request.META.get("HTTP_X_CSRFTOKEN")
            and getattr(settings, "CSRF_TRUSTED_ORIGINS", None)
        ):
            origin = settings.CSRF_TRUSTED_ORIGINS[0]
            request.META["HTTP_REFERER"] = origin

        return self.get_response(request)
