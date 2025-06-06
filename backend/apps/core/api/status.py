"""API endpoint for application status information."""
from django.conf import settings
from django.http import HttpRequest, JsonResponse
import requests

def status_view(request: HttpRequest) -> JsonResponse:
    """
    Return the current application version.
    
    Args:
        request: HTTP request object (unused but required by Django)
        
    Returns:
        JsonResponse containing the application version
    """
    if request.method != 'GET':
        return JsonResponse(
            {'error': f'Method {request.method} is not allowed'},
            status=requests.codes.method_not_allowed
        )
    version = getattr(settings, 'RELEASE_VERSION', 'unknown')
    return JsonResponse({"version": version})