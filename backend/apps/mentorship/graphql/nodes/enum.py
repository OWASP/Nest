"""GraphQL enum for Mentorship App."""

import enum

import strawberry


@strawberry.enum
class ExperienceLevelEnum(enum.Enum):
    """experience level enum."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@strawberry.enum
class ProgramStatusEnum(enum.Enum):
    """program status enum."""

    DRAFT = "draft"
    PUBLISHED = "published"
    COMPLETED = "completed"
