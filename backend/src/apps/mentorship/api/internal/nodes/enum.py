"""GraphQL enum for Mentorship App."""

import enum

import strawberry

from apps.mentorship.models import Program
from apps.mentorship.models.common.experience_level import ExperienceLevel


@strawberry.enum
class ExperienceLevelEnum(enum.Enum):
    """experience level enum."""

    BEGINNER = ExperienceLevel.ExperienceLevelChoices.BEGINNER
    INTERMEDIATE = ExperienceLevel.ExperienceLevelChoices.INTERMEDIATE
    ADVANCED = ExperienceLevel.ExperienceLevelChoices.ADVANCED
    EXPERT = ExperienceLevel.ExperienceLevelChoices.EXPERT


@strawberry.enum
class ProgramStatusEnum(enum.Enum):
    """program status enum."""

    DRAFT = Program.ProgramStatus.DRAFT
    PUBLISHED = Program.ProgramStatus.PUBLISHED
    COMPLETED = Program.ProgramStatus.COMPLETED
