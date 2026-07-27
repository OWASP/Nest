"""CSRF token API."""

from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET


@require_GET
@ensure_csrf_cookie
def get_csrf_token(request):
    """Return a response with the CSRF token."""
    response = JsonResponse({"csrftoken": get_token(request)})
    response["Cache-Control"] = "no-store"

    return response
