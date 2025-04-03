from django.http import JsonResponse
from django.middleware.csrf import get_token

def get_csrf_token(request):
    """Returns a response with the CSRF token to set it in cookies."""
    return JsonResponse({"csrftoken": get_token(request)})
    