"""Status API."""

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def get_status(request: HttpRequest) -> JsonResponse:
    """Get backend version."""
    version = getattr(settings, "RELEASE_VERSION", "unknown")
    return JsonResponse({"version": version})
