from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
import strawberry

from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum, ProgramStatusEnum
from apps.mentorship.api.internal.nodes.program import (
    CreateProgramInput,
    PaginatedPrograms,
    ProgramNode,
    UpdateProgramInput,
    UpdateProgramStatusInput,
)


class FakeProgramNode:
    def __init__(self):
        self.id = strawberry.ID("prog-1")
        self.key = "test-program"
        self.name = "Test Program"
        self.description = "A test mentorship program."
        self.domains = ["backend", "frontend"]
        self.ended_at = datetime(2026, 6, 30, tzinfo=UTC)
        self.experience_levels = [ExperienceLevelEnum.BEGINNER, ExperienceLevelEnum.INTERMEDIATE]
        self.mentees_limit = 10
        self.started_at = datetime(2026, 1, 1, tzinfo=UTC)
        self.status = ProgramStatusEnum.PUBLISHED
        self.user_role = "admin"
        self.tags = ["python", "javascript"]

        # internal manager that tests will set up
        self._admins_manager = MagicMock()

    # the real resolver code should behave similarly: return the manager's .all()
    def admins(self):
        return self._admins_manager.all()


@pytest.fixture
def mock_program_node():
    """Fixture returning a FakeProgramNode with a mocked admins manager."""
    node = FakeProgramNode()

    node._admins_manager.all.return_value = [
        MagicMock(name="admin1"),
        MagicMock(name="admin2"),
    ]

    return node


def test_program_node_fields(mock_program_node):
    """Test that ProgramNode fields are correctly assigned."""
    assert mock_program_node.id == "prog-1"
    assert mock_program_node.key == "test-program"
    assert mock_program_node.name == "Test Program"
    assert mock_program_node.description == "A test mentorship program."
    assert mock_program_node.domains == ["backend", "frontend"]
    assert mock_program_node.ended_at == datetime(2026, 6, 30, tzinfo=UTC)
    assert mock_program_node.experience_levels == [
        ExperienceLevelEnum.BEGINNER,
        ExperienceLevelEnum.INTERMEDIATE,
    ]
    assert mock_program_node.mentees_limit == 10
    assert mock_program_node.started_at == datetime(2026, 1, 1, tzinfo=UTC)
    assert mock_program_node.status == ProgramStatusEnum.PUBLISHED
    assert mock_program_node.user_role == "admin"
    assert mock_program_node.tags == ["python", "javascript"]


def test_program_node_admins(mock_program_node):
    """Test the admins resolver."""
    admins = mock_program_node.admins()
    assert len(admins) == 2


def test_paginated_programs_fields():
    """Test that PaginatedPrograms fields are correctly defined."""
    mock_programs = [MagicMock(spec=ProgramNode), MagicMock(spec=ProgramNode)]
    paginated_programs = PaginatedPrograms(current_page=1, programs=mock_programs, total_pages=5)

    assert paginated_programs.current_page == 1
    assert paginated_programs.programs == mock_programs
    assert paginated_programs.total_pages == 5


def test_create_program_input_fields():
    """Test that CreateProgramInput fields are correctly defined."""
    assert CreateProgramInput.__annotations__["name"] is str
    assert CreateProgramInput.__annotations__["description"] is str
    assert CreateProgramInput.__annotations__["domains"] == list[str]
    assert CreateProgramInput.__annotations__["ended_at"] is datetime
    assert CreateProgramInput.__annotations__["mentees_limit"] is int
    assert CreateProgramInput.__annotations__["started_at"] is datetime
    assert CreateProgramInput.__annotations__["tags"] == list[str]

    create_input = CreateProgramInput(
        name="New Program",
        description="Description for new program",
        ended_at=datetime.now(UTC),
        mentees_limit=5,
        started_at=datetime.now(UTC),
    )
    assert create_input.domains == []
    assert create_input.tags == []


def test_update_program_input_fields():
    """Test that UpdateProgramInput fields are correctly defined."""
    assert UpdateProgramInput.__annotations__["key"] is str
    assert UpdateProgramInput.__annotations__["name"] is str
    assert UpdateProgramInput.__annotations__["description"] is str
    assert UpdateProgramInput.__annotations__["admin_logins"] == list[str] | None
    assert UpdateProgramInput.__annotations__["domains"] == list[str] | None
    assert UpdateProgramInput.__annotations__["ended_at"] is datetime
    assert UpdateProgramInput.__annotations__["mentees_limit"] is int
    assert UpdateProgramInput.__annotations__["started_at"] is datetime
    assert UpdateProgramInput.__annotations__["status"] is ProgramStatusEnum
    assert UpdateProgramInput.__annotations__["tags"] == list[str] | None

    update_input = UpdateProgramInput(
        key="update-program-key",
        name="Updated Program",
        description="Updated description",
        ended_at=datetime.now(UTC),
        mentees_limit=12,
        started_at=datetime.now(UTC),
        status=ProgramStatusEnum.COMPLETED,
    )
    assert update_input.domains is None
    assert update_input.admin_logins is None
    assert update_input.tags is None


def test_update_program_status_input_fields():
    """Test that UpdateProgramStatusInput fields are correctly defined."""
    assert UpdateProgramStatusInput.__annotations__["key"] is str
    assert UpdateProgramStatusInput.__annotations__["name"] is str
    assert UpdateProgramStatusInput.__annotations__["status"] is ProgramStatusEnum
