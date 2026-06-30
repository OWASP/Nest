"""GraphQL node for Program model."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from apps.github.api.internal.dataloaders.milestone import RECENT_MILESTONES_BY_PROGRAM_ID
from apps.github.api.internal.nodes.milestone import MilestoneNode  # noqa: TC001
from apps.mentorship.api.internal.dataloaders.admin import ADMINS_BY_PROGRAM_ID_LOADER
from apps.mentorship.api.internal.nodes.enum import (
    ExperienceLevelEnum,  # noqa: TC001
    ProgramStatusEnum,  # noqa: TC001
)

# TC001/TC003: These imports must stay at runtime. Strawberry GraphQL introspects
# type annotations when building the schema; moving them under TYPE_CHECKING would
# cause UnresolvedFieldTypeError at startup.
if TYPE_CHECKING:
    from apps.mentorship.api.internal.nodes.admin import AdminNode
    from apps.mentorship.models.program import Program


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

    @strawberry_django.field
    async def admins(
        self, root: Program, info: strawberry.Info
    ) -> (
        list[Annotated[AdminNode, strawberry.lazy("apps.mentorship.api.internal.nodes.admin")]]
        | None
    ):
        """Get the list of program administrators."""
        return await info.context.mentorship_dataloaders[ADMINS_BY_PROGRAM_ID_LOADER].load(root.pk)

    @strawberry_django.field
    async def recent_milestones(self, root: Program, info: strawberry.Info) -> list[MilestoneNode]:
        """Get the list of recent milestones for the program."""
        return await info.context.github_dataloaders[RECENT_MILESTONES_BY_PROGRAM_ID].load(root.pk)


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
