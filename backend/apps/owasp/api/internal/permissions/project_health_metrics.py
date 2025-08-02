"""Strawberry Permission Classes for Project Health Metrics."""

from strawberry.permission import BasePermission


class IsOWASPStaff(BasePermission):
    """Permission class to check if the user is an OWASP staff member."""

    message = "You must be an OWASP staff member to access this resource."

    def has_permission(self, source, info, **kwargs) -> bool:
        """Check if the user is an OWASP staff member."""
        user = info.context.request.user
        return (
            user
            and hasattr(user, "github_user")
            and user.github_user
            and user.github_user.is_owasp_staff
        )
