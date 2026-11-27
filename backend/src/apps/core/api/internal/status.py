"""Status API."""

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def get_status(request: HttpRequest) -> JsonResponse:  # noqa: ARG001
    """Get backend version."""
    return JsonResponse(
        {"version": settings.RELEASE_VERSION or settings.ENVIRONMENT.lower()},
    )
