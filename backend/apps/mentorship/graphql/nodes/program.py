import strawberry
from enum import Enum
from datetime import datetime


@strawberry.type
class ProgramNode:
    id: strawberry.ID
    name: str
    description: str


@strawberry.enum
class ExperienceLevelEnum(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@strawberry.enum
class ProgramStatusEnum(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    COMPLETED = "completed"


@strawberry.input
class CreateProgramInput:
    name: str
    status: ProgramStatusEnum = ProgramStatusEnum.DRAFT
    description: str = ""
    experience_levels: list[ExperienceLevelEnum] = strawberry.field(
        default_factory=list
    )
    mentees_limit: int | None = None
    started_at: datetime
    ended_at: datetime
    domains: list[str] = strawberry.field(default_factory=list)
    tags: list[str] = strawberry.field(default_factory=list)
