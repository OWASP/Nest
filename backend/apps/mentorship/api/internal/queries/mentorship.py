"""GraphQL queries for mentorship role management."""

import strawberry

from apps.mentorship.models.mentee import Mentee
from apps.mentorship.models.mentor import Mentor
from apps.nest.api.internal.permissions import IsAuthenticated


@strawberry.type
class UserRolesResult:
    """Result type for user roles query."""

    roles: list[str]


@strawberry.type
class MentorshipQuery:
    """GraphQL queries for mentorship-related data."""

    @strawberry.field(permission_classes=[IsAuthenticated])
    def current_user_roles(self, info: strawberry.Info) -> UserRolesResult:
        """Get the mentorship roles for the currently authenticated user."""
        user = info.context.request.user

        roles = []

        if Mentee.objects.filter(nest_user=user).exists():
            roles.append("contributor")

        if Mentor.objects.filter(nest_user=user).exists():
            roles.append("mentor")

        return UserRolesResult(roles=roles)
