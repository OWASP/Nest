"""API endpoint for application status information."""
from django.conf import settings
from django.http import HttpRequest, JsonResponse


def status(request: HttpRequest) -> JsonResponse:
    """
    Return the current application version.
    
    Args:
        request: HTTP request object (unused but required by Django)
        
    Returns:
        JsonResponse containing the application version
    """
    version = getattr(settings, 'RELEASE_VERSION', 'unknown')
    return JsonResponse({"version": version})