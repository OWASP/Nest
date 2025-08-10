"""GraphQL queries for mentorship role management."""

import strawberry

from apps.github.models.user import User as GithubUser
from apps.mentorship.models.mentor import Mentor


@strawberry.type
class UserRolesResult:
    """Result type for user roles query."""

    roles: list[str]


@strawberry.type
class MentorshipQuery:
    """GraphQL queries for mentorship-related data."""

    @strawberry.field
    def is_mentor(self, login: str) -> bool:
        """Check if a GitHub login is a mentor."""
        if not login or not login.strip():
            return False

        login = login.strip()

        try:
            github_user = GithubUser.objects.get(login=login)
        except GithubUser.DoesNotExist:
            return False

        return Mentor.objects.filter(github_user=github_user).exists()
