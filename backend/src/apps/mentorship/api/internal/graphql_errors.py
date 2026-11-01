"""Shared GraphQL errors for mentorship API."""

from graphql import GraphQLError


class AuthenticationRequiredError(GraphQLError):
    """Raised when the caller must be logged in."""

    def __init__(self) -> None:
        """Build the GraphQL error with UNAUTHORIZED extension."""
        super().__init__("Authentication required.", extensions={"code": "UNAUTHORIZED"})


class ManagementProgramAccessDeniedError(GraphQLError):
    """Raised when the user cannot access management details for a program."""

    def __init__(self) -> None:
        """Build the GraphQL error with FORBIDDEN extension."""
        super().__init__(
            "You do not have permission to manage this program. Only program admins and mentors "
            "can access this view.",
            extensions={"code": "FORBIDDEN"},
        )
