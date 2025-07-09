"""Mentorship role GraphQL mutations"""

from apps.owasp.models.project import Project
import strawberry
from apps.mentorship.models import Mentee, Mentor
from apps.mentorship.utils.user import get_authenticated_user
from apps.nest.graphql.nodes.user import AuthUserNode
from django.db.models import Q


@strawberry.type
class ApplyAsRoleResult:
    success: bool
    user: AuthUserNode | None
    message: str | None


@strawberry.type
class MentorshipMutations:
    @strawberry.mutation
    def apply_as_mentee(self, info: strawberry.Info) -> ApplyAsRoleResult:
        user = get_authenticated_user(info.context.request)

        Mentee.objects.get_or_create(
            nest_user=user,
            defaults={"github_user": user.github_user},
        )

        return ApplyAsRoleResult(success=True, user=user, message="success")

    @strawberry.mutation
    def apply_as_mentor(self, info: strawberry.Info) -> ApplyAsRoleResult:
        user = get_authenticated_user(info.context.request)

        is_leader = Project.objects.filter(
            Q(leaders_raw__icontains=user.username)
            | Q(leaders_raw__icontains=user.github_user.name or "")
        ).exists()

        if not is_leader:
            return ApplyAsRoleResult(
                success=False,
                user=user,
                message="You must be a project leader to apply as a mentor.",
            )

        Mentor.objects.get_or_create(
            nest_user=user,
            defaults={"github_user": user.github_user},
        )

        return ApplyAsRoleResult(success=True, user=user, message="success")
