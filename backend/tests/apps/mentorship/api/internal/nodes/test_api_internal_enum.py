"""Pytest for mentorship enum nodes."""

from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum, ProgramStatusEnum
from apps.mentorship.models import Program
from apps.mentorship.models.common.experience_level import ExperienceLevel


def test_experience_level_enum_values():
    """Test that ExperienceLevelEnum maps correctly to model choices."""
    assert ExperienceLevelEnum.BEGINNER.value == ExperienceLevel.ExperienceLevelChoices.BEGINNER
    assert (
        ExperienceLevelEnum.INTERMEDIATE.value
        == ExperienceLevel.ExperienceLevelChoices.INTERMEDIATE
    )
    assert ExperienceLevelEnum.ADVANCED.value == ExperienceLevel.ExperienceLevelChoices.ADVANCED
    assert ExperienceLevelEnum.EXPERT.value == ExperienceLevel.ExperienceLevelChoices.EXPERT


def test_program_status_enum_values():
    """Test that ProgramStatusEnum maps correctly to model choices."""
    assert ProgramStatusEnum.DRAFT.value == Program.ProgramStatus.DRAFT
    assert ProgramStatusEnum.PUBLISHED.value == Program.ProgramStatus.PUBLISHED
    assert ProgramStatusEnum.COMPLETED.value == Program.ProgramStatus.COMPLETED
