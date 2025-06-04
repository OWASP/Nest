from django.conf import settings
from django.http import HttpRequest, JsonResponse

def status(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"version": settings.RELEASE_VERSION})