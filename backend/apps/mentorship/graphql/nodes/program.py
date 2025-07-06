"""GraphQL node for Program model."""

from datetime import datetime

import strawberry

from apps.mentorship.graphql.nodes.enum import ExperienceLevelEnum, ProgramStatusEnum
from apps.mentorship.graphql.nodes.mentor import MentorNode


@strawberry.type
class ProgramNode:
    """A mentorship program node."""

    id: strawberry.ID
    name: str
    description: str
    admins: list[MentorNode] | None = None
    domains: list[str] | None = None
    ended_at: datetime
    experience_levels: list[ExperienceLevelEnum] | None = None
    mentees_limit: int | None = None
    started_at: datetime
    status: ProgramStatusEnum
    tags: list[str] | None = None


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
    description: str = ""
    admin_logins: list[str] = strawberry.field(default_factory=list)
    domains: list[str] = strawberry.field(default_factory=list)
    ended_at: datetime
    experience_levels: list[ExperienceLevelEnum] = strawberry.field(
        default_factory=list
    )
    mentees_limit: int | None = None
    started_at: datetime
    status: ProgramStatusEnum
    tags: list[str] = strawberry.field(default_factory=list)


@strawberry.input
class UpdateProgramInput:
    """Input for updating a mentorship program."""

    id: strawberry.ID
    name: str | None = None
    description: str | None = None
    admin_logins: list[str] | None = None
    domains: list[str] | None = None
    ended_at: datetime | None = None
    experience_levels: list[ExperienceLevelEnum] | None = None
    mentees_limit: int | None = None
    started_at: datetime | None = None
    status: ProgramStatusEnum | None = None
    tags: list[str] | None = None
