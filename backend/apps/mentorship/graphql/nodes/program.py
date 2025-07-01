from datetime import datetime
from enum import Enum

import strawberry

from apps.mentorship.graphql.nodes.mentor import MentorNode


@strawberry.type
class ProgramNode:
    id: strawberry.ID
    name: str
    description: str
    status: str
    started_at: datetime
    ended_at: datetime
    experience_levels: list[str] | None = None
    mentees_limit: int | None = None
    domains: list[str] | None = None
    tags: list[str] | None = None
    admins: list[MentorNode] | None = None


@strawberry.type
class PaginatedPrograms:
    total_pages: int
    current_page: int
    programs: list[ProgramNode]


@strawberry.input
class CreateProgramInput:
    name: str
    status: str = "draft"
    description: str = ""
    experience_levels: list[str] = strawberry.field(default_factory=list)
    mentees_limit: int | None = None
    started_at: datetime
    ended_at: datetime
    domains: list[str] = strawberry.field(default_factory=list)
    tags: list[str] = strawberry.field(default_factory=list)


@strawberry.input
class UpdateProgramInput:
    id: strawberry.ID
    name: str
    description: str
    status: str
    experience_levels: list[str]
    mentees_limit: int | None = None
    started_at: datetime
    ended_at: datetime
    domains: list[str]
    tags: list[str]
    admin_logins: list[str]
