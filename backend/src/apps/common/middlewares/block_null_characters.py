"""OWASP Nest middleware to block null characters in requests."""

import logging
from http import HTTPStatus

from django.http import HttpRequest, JsonResponse

logger = logging.getLogger(__name__)

NULL_CHARACTER = "\x00"


class BlockNullCharactersMiddleware:
    """BlockNullCharactersMiddleware to block requests containing null characters."""

    def __init__(self, get_response):
        """Initialize middleware with get_response callable."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """Process the request to block null characters."""
        if (
            NULL_CHARACTER in request.path
            or NULL_CHARACTER in request.path_info
            or any(
                NULL_CHARACTER in value for values in request.GET.lists() for value in values[1]
            )
            or any(
                NULL_CHARACTER in value for values in request.POST.lists() for value in values[1]
            )
        ):
            message = (
                "Request contains null characters in URL or parameters which are not allowed."
            )
            logger.warning(message)
            return JsonResponse({"message": message, "errors": {}}, status=HTTPStatus.BAD_REQUEST)

        content_length = int(request.META.get("CONTENT_LENGTH", 0) or 0)
        if content_length and (b"\x00" in request.body or b"\\u0000" in request.body):
            message = "Request contains null characters in body which are not allowed."
            logger.warning(message)
            return JsonResponse({"message": message, "errors": {}}, status=HTTPStatus.BAD_REQUEST)

        return self.get_response(request)
