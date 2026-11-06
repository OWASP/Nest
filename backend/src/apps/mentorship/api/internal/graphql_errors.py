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


class MentorshipPermissionDeniedError(GraphQLError):
    """Raised when user lacks permission for a mentorship mutation or action."""

    def __init__(self, message: str = "Permission denied.") -> None:
        """Build the GraphQL error with FORBIDDEN extension."""
        super().__init__(message, extensions={"code": "FORBIDDEN"})


class MentorshipValidationError(GraphQLError):
    """Raised when validation fails on a mentorship mutation input."""

    def __init__(self, message: str, field: str | None = None) -> None:
        """Build the GraphQL error with VALIDATION_ERROR extension."""
        extensions: dict[str, str] = {"code": "VALIDATION_ERROR"}
        if field:
            extensions["field"] = field
        super().__init__(message, extensions=extensions)


class MentorshipNotFoundError(GraphQLError):
    """Raised when a requested mentorship entity (program, module, project, etc.) is not found."""

    def __init__(self, message: str = "Object not found.") -> None:
        """Build the GraphQL error with NOT_FOUND extension."""
        super().__init__(message, extensions={"code": "NOT_FOUND"})

