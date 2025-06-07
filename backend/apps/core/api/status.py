"""API endpoint for application status information."""

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def get_status(_request: HttpRequest) -> JsonResponse:
    """Return the current application version.

    Args:
        _request: HTTP request object (unused)

    Returns:
        JsonResponse containing the application version

    """
    return JsonResponse(
        {
            "version": settings.RELEASE_VERSION or settings.ENVIRONMENT.lower(),
        }
    )
