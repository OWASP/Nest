"""Tests for tag validation logic."""

from datetime import UTC, datetime

import pytest
import strawberry

from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum, ProgramStatusEnum
from apps.mentorship.api.internal.nodes.module import CreateModuleInput, UpdateModuleInput
from apps.mentorship.api.internal.nodes.program import CreateProgramInput, UpdateProgramInput
from apps.mentorship.api.internal.utils import validate_tags


def test_validate_tags_valid():
    """Test valid tags."""
    tags = ["python", "Django", "123"]
    assert validate_tags(tags) == tags


def test_validate_tags_duplicates():
    """Test duplicate tags raise error."""
    tags = ["python", "python"]
    with pytest.raises(ValueError, match="Tags must be unique"):
        validate_tags(tags)


def test_validate_tags_invalid_format():
    """Test invalid tag format raises error."""
    tags = ["python code"]
    with pytest.raises(ValueError, match="must be alphanumeric"):
        validate_tags(tags)

    tags = ["python-django"]
    with pytest.raises(ValueError, match="must be alphanumeric"):
        validate_tags(tags)

    tags = ["<script>"]
    with pytest.raises(ValueError, match="must be alphanumeric"):
        validate_tags(tags)


def test_validate_domains_valid():
    """Test valid domains."""
    from apps.mentorship.api.internal.utils import validate_domains

    domains = ["App Sec", "Web Security", "AI"]
    assert validate_domains(domains) == domains


def test_validate_domains_duplicates():
    """Test duplicate domains raise error."""
    from apps.mentorship.api.internal.utils import validate_domains

    domains = ["AppSec", "AppSec"]
    with pytest.raises(ValueError, match="Domains must be unique"):
        validate_domains(domains)


def test_validate_domains_invalid_format():
    """Test invalid domain format raises error."""
    from apps.mentorship.api.internal.utils import validate_domains

    domains = ["App@Sec"]
    with pytest.raises(ValueError, match="must be alphanumeric"):
        validate_domains(domains)

    domains = ["<script>"]
    with pytest.raises(ValueError, match="must be alphanumeric"):
        validate_domains(domains)


def test_program_input_validation():
    """Test program inputs trigger validation."""
    now = datetime.now(tz=UTC)

    CreateProgramInput(
        name="Test",
        description="Desc",
        ended_at=now,
        mentees_limit=1,
        started_at=now,
        tags=["Valid1"],
        domains=["Valid Domain"],
    )

    with pytest.raises(ValueError, match="must be alphanumeric"):
        CreateProgramInput(
            name="Test",
            description="Desc",
            ended_at=now,
            mentees_limit=1,
            started_at=now,
            tags=["Invalid Space"],
        )

    with pytest.raises(ValueError, match="must be alphanumeric"):
        CreateProgramInput(
            name="Test",
            description="Desc",
            ended_at=now,
            mentees_limit=1,
            started_at=now,
            domains=["Invalid@Domain"],
        )

    UpdateProgramInput(
        key="key",
        name="Test",
        description="Desc",
        ended_at=now,
        mentees_limit=1,
        started_at=now,
        status=ProgramStatusEnum.PUBLISHED,
        tags=["Valid2"],
        domains=["Valid Domain"],
    )


def test_module_input_validation():
    """Test module inputs trigger validation."""
    now = datetime.now(tz=UTC)
    pid = strawberry.ID("1")
    CreateModuleInput(
        name="Test",
        description="Desc",
        ended_at=now,
        experience_level=ExperienceLevelEnum.BEGINNER,
        program_key="prog",
        project_name="proj",
        project_id=pid,
        started_at=now,
        tags=["Valid3"],
        domains=["Valid Domain"],
    )
    with pytest.raises(ValueError, match="must be alphanumeric"):
        CreateModuleInput(
            name="Test",
            description="Desc",
            ended_at=now,
            experience_level=ExperienceLevelEnum.BEGINNER,
            program_key="prog",
            project_name="proj",
            project_id=pid,
            started_at=now,
            tags=["Valid3"],
            domains=["Invalid@Domain"],
        )

    UpdateModuleInput(
        key="mod-key",
        program_key="prog",
        name="Test",
        description="Desc",
        ended_at=now,
        experience_level=ExperienceLevelEnum.BEGINNER,
        project_id=pid,
        project_name="proj",
        started_at=now,
        tags=["Valid4"],
        domains=["Valid Domain"],
    )

    with pytest.raises(ValueError, match="must be alphanumeric"):
        UpdateModuleInput(
            key="mod-key",
            program_key="prog",
            name="Test",
            description="Desc",
            ended_at=now,
            experience_level=ExperienceLevelEnum.BEGINNER,
            project_id=pid,
            project_name="proj",
            started_at=now,
            tags=["invalid space"],
        )
