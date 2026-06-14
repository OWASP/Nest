"""GraphQL node for Program model."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING, Annotated

import strawberry

from apps.github.api.internal.nodes.milestone import MilestoneNode  # noqa: TC001
from apps.github.models.milestone import Milestone
from apps.mentorship.api.internal.nodes.enum import (
    ExperienceLevelEnum,  # noqa: TC001
    ProgramStatusEnum,  # noqa: TC001
)
from apps.mentorship.api.internal.utils import validate_domains, validate_tags

# TC001/TC003: These imports must stay at runtime. Strawberry GraphQL introspects
# type annotations when building the schema; moving them under TYPE_CHECKING would
# cause UnresolvedFieldTypeError at startup.
if TYPE_CHECKING:
    from apps.mentorship.api.internal.nodes.admin import AdminNode


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
    def admins(
        self,
    ) -> (
        list[Annotated[AdminNode, strawberry.lazy("apps.mentorship.api.internal.nodes.admin")]]
        | None
    ):
        """Get the list of program administrators."""
        return self.admins.order_by("github_user__login")

    @strawberry.field
    def recent_milestones(self) -> list[MilestoneNode]:
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

    def __post_init__(self):
        """Validate input."""
        if self.tags:
            validate_tags(self.tags)
        if self.domains:
            validate_domains(self.domains)


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

    def __post_init__(self):
        """Validate input."""
        if self.tags:
            validate_tags(self.tags)
        if self.domains:
            validate_domains(self.domains)


@strawberry.input
class UpdateProgramStatusInput:
    """Input for updating program status."""

    key: str
    name: str
    status: ProgramStatusEnum
