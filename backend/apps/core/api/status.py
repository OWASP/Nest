from django.conf import settings
from django.http import JsonResponse

def status_view(request):
    """Return backend status and version."""
    return JsonResponse({
        "status": "ok",
        "version": getattr(settings, "RELEASE_VERSION", None),
    })
