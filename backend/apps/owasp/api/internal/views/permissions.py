"""Permissions for OWASP API views."""

from functools import wraps

from django.contrib.auth import get_user
from django.http import HttpResponseForbidden


def has_dashboard_permission(request):
    """Check if user has dashboard access."""
    # Returns Anonymous user even if authenticated
    # Strawberry returns the authenticated user
    user = get_user(request)
    return (
        user
        and hasattr(user, "github_user")
        and user.github_user
        and user.github_user.is_owasp_staff
    )


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
