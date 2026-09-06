"""E2E-only views."""

import json

from django.conf import settings
from django.contrib.auth import login
from django.http import Http404, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.nest.models import User

E2E_ALLOWED_USERS = frozenset({"e2e-user", "e2e-mentor", "e2e-mentee"})


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

    raw_username = payload.get("username")
    if not isinstance(raw_username, str) or not raw_username.strip():
        return JsonResponse({"message": "username is required.", "ok": False}, status=400)

    username = raw_username.strip()
    if username not in E2E_ALLOWED_USERS:
        raise Http404

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist as exc:
        raise Http404 from exc

    login(request, user)

    return JsonResponse({"ok": True, "username": username})
