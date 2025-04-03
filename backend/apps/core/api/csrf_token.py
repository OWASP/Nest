"""CSRF token API."""

from django.http import JsonResponse
from django.middleware.csrf import get_token


def get_csrf_token(request):
    """Return a response with the CSRF token."""
    return JsonResponse({"csrftoken": get_token(request)})
