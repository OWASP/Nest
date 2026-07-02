"""GraphQL permissions classes for authentication."""

from typing import Any

from graphql import GraphQLError
from strawberry.permission import BasePermission
from strawberry.types import Info


class IsAuthenticated(BasePermission):
    """Permission class to check if the user is authenticated."""

    message = "You must be logged in to perform this action."

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        """Check if the user is authenticated."""
        return info.context.request.user.is_authenticated

    def on_unauthorized(self) -> Any:
        """Handle unauthorized access."""
        return GraphQLError(self.message, extensions={"code": "UNAUTHORIZED"})
