"""Permissions for OWASP API views."""

from functools import wraps

from django.conf import settings
from django.http import HttpResponseForbidden


def has_dashboard_permission(request):
    """Check if user has dashboard access."""
    return (
        True
        if settings.IS_E2E_ENVIRONMENT or settings.IS_FUZZ_ENVIRONMENT
        else (
            (user := request.user)
            and user.is_authenticated
            and (
                user.github_user.owasp_profile.is_owasp_staff
                if hasattr(user.github_user, "owasp_profile")
                else user.github_user.is_owasp_staff
            )
        )
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
