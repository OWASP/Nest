"""Mentorship role GraphQL mutations."""

import strawberry
from django.db import transaction
from django.db.models import Q

from apps.mentorship.models import Mentee, Mentor
from apps.nest.api.internal.nodes.user import AuthUserNode
from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.models.project import Project


@strawberry.type
class ApplyAsRoleResult:
    """Represent the result of a user applying for a role."""

    success: bool
    user: AuthUserNode | None
    message: str | None


@strawberry.type
class MentorshipMutations:
    """GraphQL mutations related to the mentorship module."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def apply_as_mentee(self, info: strawberry.Info) -> ApplyAsRoleResult:
        """Register the authenticated user as a mentee."""
        user = info.context.request.user
        IsAuthenticated.require_github_user(user)

        Mentee.objects.get_or_create(
            nest_user=user,
            defaults={"github_user": user.github_user},
        )

        return ApplyAsRoleResult(
            success=True, user=user, message="Successfully registered as a mentee."
        )

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def apply_as_mentor(self, info: strawberry.Info) -> ApplyAsRoleResult:
        """Check for project leadership and register the user as a mentor."""
        user = info.context.request.user
        IsAuthenticated.require_github_user(user)

        github_user = user.github_user

        is_leader = Project.objects.filter(
            Q(leaders_raw__icontains=github_user.login)
            | Q(leaders_raw__icontains=github_user.name or "")
        ).exists()

        if not is_leader:
            return ApplyAsRoleResult(
                success=False,
                user=user,
                message="You must be a project leader to apply as a mentor.",
            )

        Mentor.objects.get_or_create(
            nest_user=user,
            defaults={"github_user": github_user},
        )

        return ApplyAsRoleResult(
            success=True, user=user, message="Successfully registered as a mentor."
        )
