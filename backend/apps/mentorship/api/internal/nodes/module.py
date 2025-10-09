"""GraphQL nodes for Module model."""

from datetime import datetime

import strawberry

from apps.github.api.internal.nodes.issue import IssueNode
from apps.github.api.internal.nodes.user import UserNode
from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum
from apps.mentorship.api.internal.nodes.mentor import MentorNode
from apps.mentorship.api.internal.nodes.program import ProgramNode
from apps.mentorship.models.issue_user_interest import IssueUserInterest
from apps.mentorship.models.task import Task


@strawberry.type
class ModuleNode:
    """A GraphQL node representing a mentorship module."""

    id: strawberry.ID
    key: str
    name: str
    description: str
    domains: list[str] | None = None
    ended_at: datetime
    experience_level: ExperienceLevelEnum
    labels: list[str] | None = None
    program: ProgramNode | None = None
    project_id: strawberry.ID | None = None
    started_at: datetime
    tags: list[str] | None = None

    @strawberry.field
    def mentors(self) -> list[MentorNode]:
        """Get the list of mentors for this module."""
        return self.mentors.all()

    @strawberry.field
    def project_name(self) -> str | None:
        """Get the project name for this module."""
        return self.project.name if self.project else None

    @strawberry.field
    def issues(self) -> list[IssueNode]:
        """Return issues linked to this module."""
        return list(
            self.issues.select_related("repository", "author")
            .prefetch_related("assignees", "labels")
            .order_by("-created_at")
        )

    @strawberry.field
    def issue_by_number(self, number: int) -> IssueNode | None:
        """Return a single issue by its GitHub number within this module's linked issues."""
        return (
            self.issues.select_related("repository", "author")
            .prefetch_related("assignees", "labels")
            .filter(number=number)
            .first()
        )

    @strawberry.field
    def interested_users(self, issue_number: int) -> list[UserNode]:
        """Return users interested in this module's issue identified by its number."""
        issue_ids = list(self.issues.filter(number=issue_number).values_list("id", flat=True))
        if not issue_ids:
            return []
        interests = (
            IssueUserInterest.objects.select_related("user")
            .filter(module=self, issue_id__in=issue_ids)
            .order_by("user__login")
        )
        return [i.user for i in interests]

    @strawberry.field
    def task_deadline(self, issue_number: int) -> datetime | None:
        """Return the earliest deadline for tasks linked to this module and issue number."""
        return (
            Task.objects.filter(
                module=self,
                issue__number=issue_number,
                deadline_at__isnull=False,
            )
            .order_by("deadline_at")
            .values_list("deadline_at", flat=True)
            .first()
        )

    @strawberry.field
    def task_assigned_at(self, issue_number: int) -> datetime | None:
        """Return the earliest assignment time for tasks linked to this module and issue number."""
        return (
            Task.objects.filter(
                module=self,
                issue__number=issue_number,
                assigned_at__isnull=False,
            )
            .order_by("assigned_at")
            .values_list("assigned_at", flat=True)
            .first()
        )


@strawberry.input
class CreateModuleInput:
    """Input for creating a mentorship module."""

    name: str
    description: str
    domains: list[str] = strawberry.field(default_factory=list)
    ended_at: datetime
    experience_level: ExperienceLevelEnum
    labels: list[str] = strawberry.field(default_factory=list)
    mentor_logins: list[str] | None = None
    program_key: str
    project_name: str
    project_id: strawberry.ID
    started_at: datetime
    tags: list[str] = strawberry.field(default_factory=list)


@strawberry.input
class UpdateModuleInput:
    """Input for updating a mentorship module."""

    key: str
    program_key: str
    name: str
    description: str
    domains: list[str] = strawberry.field(default_factory=list)
    ended_at: datetime
    experience_level: ExperienceLevelEnum
    labels: list[str] = strawberry.field(default_factory=list)
    mentor_logins: list[str] | None = None
    project_id: strawberry.ID
    project_name: str
    started_at: datetime
    tags: list[str] = strawberry.field(default_factory=list)
