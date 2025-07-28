"""GraphQL nodes for Module model."""

from datetime import datetime

import strawberry

from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum
from apps.mentorship.api.internal.nodes.mentor import MentorNode
from apps.mentorship.api.internal.nodes.program import ProgramNode


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


@strawberry.input
class CreateModuleInput:
    """Input for creating a mentorship module."""

    name: str
    description: str
    domains: list[str] = strawberry.field(default_factory=list)
    ended_at: datetime
    experience_level: ExperienceLevelEnum
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
    mentor_logins: list[str] | None = None
    project_id: strawberry.ID
    project_name: str
    started_at: datetime
    tags: list[str] = strawberry.field(default_factory=list)
