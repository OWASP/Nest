"""Permissions for OWASP API views."""

from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden


def has_dashboard_permission(request):
    """Check if user has dashboard access."""
    user = getattr(request, "user", None)
    if not (user and user.is_authenticated and hasattr(user, "github_user")):
        return False
    try:
        github_user = user.github_user
    except ObjectDoesNotExist:
        return False

    try:
        profile = github_user.owasp_profile
    except ObjectDoesNotExist:
        return False

    return bool(getattr(profile, "is_owasp_staff", False))


def dashboard_access_required(view_func):
    """Require dashboard access permission.

    Args:
        view_func: The view function to wrap.

    Returns:
        The wrapped view function that checks for dashboard access permission.

    """

    @wraps(view_func)
    def _wrapper(request, *args, **kwargs):
        if not has_dashboard_permission(request):
            return HttpResponseForbidden("You must have dashboard access to access this resource.")
        return view_func(request, *args, **kwargs)

    return _wrapper
