"""OWASP Nest middleware to block null characters in requests."""

import logging

from django.http import HttpRequest, JsonResponse

logger = logging.getLogger(__name__)


class BlockNullCharactersMiddleware:
    """BlockNullCharactersMiddleware to block requests containing null characters."""

    def __init__(self, get_response):
        """Initialize middleware with get_response callable."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """Process the request to block null characters."""
        error_response = JsonResponse(
            {"error": "Request contains null characters which are not allowed."},
            status=400,
        )
        if (
            "\x00" in request.path
            or "\x00" in request.path_info
            or any("\x00" in value for values in request.GET.lists() for value in values[1])
            or any("\x00" in value for values in request.POST.lists() for value in values[1])
        ):
            logger.warning("Blocked request with null character in URL or parameters.")
            return error_response

        content_length = int(request.META.get("CONTENT_LENGTH", 0) or 0)
        if content_length > 0 and (b"\x00" in request.body or b"\\u0000" in request.body):
            logger.warning("Blocked request with null character in body.")
            return error_response

        return self.get_response(request)
