"""E2E-only login view."""

import json

from django.conf import settings
from django.contrib.auth import login
from django.http import Http404, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.nest.models import User


@csrf_exempt  # NOSONAR
@require_POST
def e2e_login(request: HttpRequest) -> JsonResponse:
    """Log in a seeded e2e user and set the Django session cookie."""
    if not settings.IS_E2E_ENVIRONMENT:
        raise Http404

    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON.", "ok": False}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({"message": "Invalid JSON.", "ok": False}, status=400)

    username = (payload.get("username") or "").strip()
    if not username:
        return JsonResponse({"message": "username is required.", "ok": False}, status=400)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist as exc:
        raise Http404 from exc

    login(request, user)

    return JsonResponse({"ok": True, "username": username})
