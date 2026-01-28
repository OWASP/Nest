"""GraphQL node for Program model."""

from datetime import datetime

import strawberry

from apps.github.api.internal.nodes.milestone import MilestoneNode  # noqa: TC001
from apps.github.models.milestone import Milestone
from apps.mentorship.api.internal.nodes.admin import AdminNode
from apps.mentorship.api.internal.nodes.enum import (
    ExperienceLevelEnum,
    ProgramStatusEnum,
)


@strawberry.type
class ProgramNode:
    """A mentorship program node."""

    id: strawberry.ID
    key: str
    name: str
    description: str
    domains: list[str] | None = None
    ended_at: datetime
    experience_levels: list[ExperienceLevelEnum] | None = None
    mentees_limit: int | None = None
    started_at: datetime
    status: ProgramStatusEnum
    user_role: str | None = None
    tags: list[str] | None = None

    @strawberry.field
    def admins(self) -> list[AdminNode] | None:
        """Get the list of program administrators."""
        return list(self.admins.all()) or None

    @strawberry.field
    def recent_milestones(self) -> list["MilestoneNode"]:
        """Get the list of recent milestones for the program."""
        project_ids = self.modules.values_list("project_id", flat=True)

        return (
            Milestone.open_milestones.filter(repository__project__in=project_ids)
            .select_related("repository__organization", "author")
            .prefetch_related("labels")
            .order_by("-created_at")
            .distinct()
        )


@strawberry.type
class PaginatedPrograms:
    """A paginated list of mentorship programs."""

    current_page: int
    programs: list[ProgramNode]
    total_pages: int


@strawberry.input
class CreateProgramInput:
    """Input Node for creating a mentorship program."""

    name: str
    description: str
    domains: list[str] = strawberry.field(default_factory=list)
    ended_at: datetime
    mentees_limit: int
    started_at: datetime
    tags: list[str] = strawberry.field(default_factory=list)


@strawberry.input
class UpdateProgramInput:
    """Input for updating a mentorship program."""

    key: str
    name: str
    description: str
    admin_logins: list[str] | None = None
    domains: list[str] | None = None
    ended_at: datetime
    mentees_limit: int
    started_at: datetime
    status: ProgramStatusEnum
    tags: list[str] | None = None


@strawberry.input
class UpdateProgramStatusInput:
    """Input for updating program status."""

    key: str
    name: str
    status: ProgramStatusEnum
