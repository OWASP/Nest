"""GraphQL queries for mentorship role management."""

import strawberry
from django.core.exceptions import ObjectDoesNotExist

from apps.mentorship.models.mentee import Mentee
from apps.mentorship.models.mentor import Mentor
from apps.mentorship.utils.user import get_user_entities_by_github_username
from apps.nest.graphql.permissions import IsAuthenticated


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
        username = info.context.request.user

        user_entities = get_user_entities_by_github_username(username)

        if not user_entities:
            msg = "Logic error: Authenticated user not found in the database."
            raise ObjectDoesNotExist(msg)

        github_user, user = user_entities
        roles = []

        if Mentee.objects.filter(nest_user=user).exists():
            roles.append("contributor")

        if Mentor.objects.filter(nest_user=user).exists():
            roles.append("mentor")

        return UserRolesResult(roles=roles)
