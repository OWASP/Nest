"""Permissions for OWASP API views."""

from functools import wraps

from django.http import HttpResponseForbidden


def has_owasp_staff_permission(user):
    """Check if user is an OWASP staff member."""
    return (
        user
        and hasattr(user, "github_user")
        and user.github_user
        and user.github_user.is_owasp_staff
    )


def owasp_staff_required(view_func):
    """Require OWASP staff permission.

    Args:
        view_func: The view function to wrap.

    Returns:
        The wrapped view function that checks for OWASP staff permission.

    """

    @wraps(view_func)
    def _wrapper(request, *args, **kwargs):
        if not has_owasp_staff_permission(request.user):
            return HttpResponseForbidden(
                "You must be an OWASP staff member to access this resource."
            )
        return view_func(request, *args, **kwargs)

    return _wrapper
