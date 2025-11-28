"""GraphQL queries for mentorship role management."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import strawberry
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.models import Label
from apps.github.models.user import User as GithubUser
from apps.mentorship.api.internal.nodes.mentee import MenteeNode
from apps.mentorship.models import Module
from apps.mentorship.models.mentee import Mentee
from apps.mentorship.models.mentee_module import MenteeModule
from apps.mentorship.models.mentor import Mentor

if TYPE_CHECKING:
    from apps.github.api.internal.nodes.issue import IssueNode


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

    @strawberry.field
    def get_mentee_details(self, program_key: str, module_key: str, mentee_key: str) -> MenteeNode:
        """Get detailed information about a mentee in a specific module."""
        try:
            module = Module.objects.only("id").get(key=module_key, program__key=program_key)

            github_user = GithubUser.objects.only("login", "name", "avatar_url", "bio").get(
                login=mentee_key
            )

            mentee = Mentee.objects.only("id", "experience_level", "domains", "tags").get(
                github_user=github_user
            )
            is_enrolled = MenteeModule.objects.filter(mentee=mentee, module=module).exists()

            if not is_enrolled:
                message = f"Mentee {mentee_key} is not enrolled in module {module_key}"
                raise ObjectDoesNotExist(message)

            return MenteeNode(
                id=cast("strawberry.ID", str(mentee.id)),
                login=github_user.login,
                name=github_user.name or github_user.login,
                avatar_url=github_user.avatar_url,
                bio=github_user.bio,
                experience_level=mentee.experience_level,
                domains=mentee.domains,
                tags=mentee.tags,
            )

        except (Module.DoesNotExist, GithubUser.DoesNotExist, Mentee.DoesNotExist) as e:
            message = f"Mentee details not found: {e}"
            raise ObjectDoesNotExist(message) from e

    @strawberry.field
    def get_mentee_module_issues(
        self,
        program_key: str,
        module_key: str,
        mentee_key: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[IssueNode]:
        """Get issues assigned to a mentee in a specific module."""
        try:
            module = Module.objects.only("id").get(key=module_key, program__key=program_key)

            github_user = GithubUser.objects.only("id").get(login=mentee_key)

            mentee = Mentee.objects.only("id").get(github_user=github_user)
            is_enrolled = MenteeModule.objects.filter(mentee=mentee, module=module).exists()

            if not is_enrolled:
                message = f"Mentee {mentee_key} is not enrolled in module {module_key}"
                raise ObjectDoesNotExist(message)

            issues_qs = (
                module.issues.filter(assignees=github_user)
                .only("id", "number", "title", "state", "created_at", "url")
                .prefetch_related(
                    Prefetch("labels", queryset=Label.objects.only("id", "name")),
                    Prefetch(
                        "assignees",
                        queryset=GithubUser.objects.only("id", "login", "name", "avatar_url"),
                    ),
                )
                .order_by("-created_at")
            )
            issues = issues_qs[offset : offset + limit]

            return list(issues)

        except (Module.DoesNotExist, GithubUser.DoesNotExist, Mentee.DoesNotExist) as e:
            message = f"Mentee issues not found: {e}"
            raise ObjectDoesNotExist(message) from e
