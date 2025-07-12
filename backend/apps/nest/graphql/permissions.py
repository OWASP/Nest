"""Permission module for GraphQL resolvers."""

from typing import Any

from django.core.exceptions import PermissionDenied
from strawberry.permission import BasePermission
from strawberry.types import Info


class IsAuthenticated(BasePermission):
    """Permission class to check if the user is authenticated."""

    message = "You must be logged in to perform this action."

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        """Check if the user is authenticated.

        Args:
            source: The root object of the GraphQL resolver.
            info (Info): The GraphQL resolver info, containing context like request.
            **kwargs: Additional arguments passed to the resolver.

        Returns:
            bool: True if the user is authenticated, otherwise False.

        """
        return info.context.request.user.is_authenticated

    def on_unauthorized(self) -> Any | None:
        """Handle unauthorized access when permission is denied.

        Raises:
            PermissionDenied: If the user is not authenticated.

        """
        raise PermissionDenied(self.message)
