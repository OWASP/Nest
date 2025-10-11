"""Strawberry Permission Classes for Project Health Metrics."""

from strawberry.permission import BasePermission


class HasDashboardAccess(BasePermission):
    """Permission class to check if the user has dashboard access."""

    message = "You must have dashboard access to access this resource."

    def has_permission(self, source, info, **kwargs) -> bool:
        """Check if the user has dashboard access."""
        return (
            (user := info.context.request.user)
            and user.is_authenticated
            and user.github_user.is_owasp_staff
        )
