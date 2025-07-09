import strawberry
from apps.mentorship.models.mentee import Mentee
from apps.mentorship.models.mentor import Mentor
from apps.mentorship.utils.user import get_authenticated_user_by_token


@strawberry.type
class UserRolesResult:
    roles: list[str]


@strawberry.type
class MentorshipQuery:
    @strawberry.field
    def current_user_roles(self, access_token: str) -> UserRolesResult:
        user = get_authenticated_user_by_token(access_token)

        roles = []

        if Mentee.objects.filter(nest_user=user).exists():
            roles.append("contributor")

        if Mentor.objects.filter(nest_user=user).exists():
            roles.append("mentor")

        return UserRolesResult(roles=roles)
