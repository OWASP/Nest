"""Pytest for mentorship program mutations."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError

from apps.mentorship.api.internal.mutations.program import ProgramMutation
from apps.mentorship.api.internal.nodes.enum import ProgramStatusEnum


@pytest.fixture
def mock_github_user():
    """Fixture for a mock GithubUser."""
    mock = MagicMock()
    mock.login = "testuser"
    mock.save = MagicMock()
    return mock


@pytest.fixture
def mock_nest_user(mock_github_user):
    """Fixture for a mock Nest User."""
    mock = MagicMock()
    mock.username = "testuser"
    mock.github_user = mock_github_user
    return mock


@pytest.fixture
def mock_mentor(mock_nest_user, mock_github_user):
    """Fixture for a mock Mentor."""
    mock = MagicMock()
    mock.id = 1
    mock.nest_user = mock_nest_user
    mock.github_user = mock_github_user
    mock.save = MagicMock()
    return mock


@pytest.fixture
def mock_program():
    """Fixture for a mock Program."""
    mock = MagicMock()
    mock.key = "program-key"
    mock.name = "Test Program"
    mock.admins.filter.return_value.exists.return_value = True
    mock.save = MagicMock()
    return mock


@pytest.fixture
def mock_info(mock_nest_user):
    """Fixture for a mock Strawberry Info object."""
    mock = MagicMock()
    mock.context.request.user = mock_nest_user
    return mock


# Tests for create_program
@patch("apps.mentorship.api.internal.mutations.program.Mentor")
@patch("apps.mentorship.api.internal.mutations.program.Program")
def test_create_program_success(
    MockProgram, MockMentor, mock_info, mock_mentor, mock_nest_user
):
    """Test successful creation of a program."""
    MockMentor.objects.get_or_create.return_value = (mock_mentor, True)
    MockProgram.objects.create.return_value = mock_program

    input_data = MagicMock(
        name="New Program",
        description="Description",
        mentees_limit=10,
        started_at=datetime(2025, 1, 1),
        ended_at=datetime(2025, 12, 31),
        domains=[],
        tags=[],
    )

    mutation = ProgramMutation()
    result = mutation.create_program(mock_info, input_data)

    MockMentor.objects.get_or_create.assert_called_once_with(
        nest_user=mock_nest_user, defaults={"github_user": mock_nest_user.github_user}
    )
    MockProgram.objects.create.assert_called_once_with(
        name=input_data.name,
        description=input_data.description,
        mentees_limit=input_data.mentees_limit,
        started_at=input_data.started_at,
        ended_at=input_data.ended_at,
        domains=input_data.domains,
        tags=input_data.tags,
        status=ProgramStatusEnum.DRAFT.value,
    )
    mock_program.admins.set.assert_called_once_with([mock_mentor])
    assert result == mock_program


@patch("apps.mentorship.api.internal.mutations.program.Mentor")
def test_create_program_end_before_start(MockMentor, mock_info, mock_mentor, mock_nest_user):
    """Test create_program fails if end date is before start date."""
    MockMentor.objects.get_or_create.return_value = (mock_mentor, True)

    input_data = MagicMock(
        name="New Program",
        description="Description",
        mentees_limit=10,
        started_at=datetime(2025, 12, 31),
        ended_at=datetime(2025, 1, 1),
        domains=[],
        tags=[],
    )

    mutation = ProgramMutation()
    with pytest.raises(ValidationError, match="End date must be after start date."):
        mutation.create_program(mock_info, input_data)


# Tests for update_program
@patch("apps.mentorship.api.internal.mutations.program.Program")
@patch("apps.mentorship.api.internal.mutations.program.Mentor")
@patch("apps.mentorship.api.internal.mutations.program.resolve_mentors_from_logins")
def test_update_program_success(
    mock_resolve_mentors,
    MockMentor,
    MockProgram,
    mock_info,
    mock_program,
    mock_mentor,
):
    """Test successful update of a program."""
    MockProgram.objects.get.return_value = mock_program
    MockMentor.objects.get.return_value = mock_mentor
    mock_program.admins.filter.return_value.exists.return_value = True
    mock_resolve_mentors.return_value = {mock_mentor}

    input_data = MagicMock(
        key="program-key",
        name="Updated Program",
        description="Updated Description",
        mentees_limit=20,
        started_at=datetime(2025, 1, 15),
        ended_at=datetime(2025, 11, 15),
        domains=["security"],
        tags=["graphql"],
        status=ProgramStatusEnum.PUBLISHED,
        admin_logins=["admin1"],
    )

    mutation = ProgramMutation()
    result = mutation.update_program(mock_info, input_data)

    MockProgram.objects.get.assert_called_once_with(key="program-key")
    MockMentor.objects.get.assert_called_once_with(nest_user=mock_info.context.request.user)
    mock_program.admins.filter.assert_called_once_with(id=mock_mentor.id)
    assert mock_program.name == "Updated Program"
    assert mock_program.description == "Updated Description"
    assert mock_program.mentees_limit == 20
    assert mock_program.started_at == datetime(2025, 1, 15)
    assert mock_program.ended_at == datetime(2025, 11, 15)
    assert mock_program.domains == ["security"]
    assert mock_program.tags == ["graphql"]
    assert mock_program.status == ProgramStatusEnum.PUBLISHED.value
    mock_program.save.assert_called_once()
    mock_resolve_mentors.assert_called_once_with(input_data.admin_logins)
    mock_program.admins.set.assert_called_once_with({mock_mentor})
    assert result == mock_program


@patch("apps.mentorship.api.internal.mutations.program.Program")
def test_update_program_not_found(MockProgram, mock_info):
    """Test update_program fails if program is not found."""
    MockProgram.objects.get.side_effect = ObjectDoesNotExist

    input_data = MagicMock(key="nonexistent")
    mutation = ProgramMutation()
    with pytest.raises(ObjectDoesNotExist, match="Program with key 'nonexistent' not found."):
        mutation.update_program(mock_info, input_data)


@patch("apps.mentorship.api.internal.mutations.program.Program")
@patch("apps.mentorship.api.internal.mutations.program.Mentor")
def test_update_program_not_mentor(MockMentor, MockProgram, mock_info, mock_program):
    """Test update_program fails if user is not a mentor."""
    MockProgram.objects.get.return_value = mock_program
    MockMentor.objects.get.side_effect = ObjectDoesNotExist

    input_data = MagicMock(key="program-key")
    mutation = ProgramMutation()
    with pytest.raises(PermissionDenied, match="You must be a mentor to update a program."):
        mutation.update_program(mock_info, input_data)


@patch("apps.mentorship.api.internal.mutations.program.Program")
@patch("apps.mentorship.api.internal.mutations.program.Mentor")
def test_update_program_not_admin(
    MockMentor, MockProgram, mock_info, mock_program, mock_mentor
):
    """Test update_program fails if user is not a program admin."""
    MockProgram.objects.get.return_value = mock_program
    MockMentor.objects.get.return_value = mock_mentor
    mock_program.admins.filter.return_value.exists.return_value = False

    input_data = MagicMock(key="program-key")
    mutation = ProgramMutation()
    with pytest.raises(PermissionDenied, match="You must be an admin of this program to update it."):
        mutation.update_program(mock_info, input_data)


@patch("apps.mentorship.api.internal.mutations.program.Program")
@patch("apps.mentorship.api.internal.mutations.program.Mentor")
def test_update_program_end_before_start(
    MockMentor, MockProgram, mock_info, mock_program, mock_mentor
):
    """Test update_program fails if end date is before start date."""
    MockProgram.objects.get.return_value = mock_program
    MockMentor.objects.get.return_value = mock_mentor
    mock_program.admins.filter.return_value.exists.return_value = True

    input_data = MagicMock(
        key="program-key",
        started_at=datetime(2025, 12, 31),
        ended_at=datetime(2025, 1, 1),
    )

    mutation = ProgramMutation()
    with pytest.raises(ValidationError, match="End date must be after start date."):
        mutation.update_program(mock_info, input_data)


# Tests for update_program_status
@patch("apps.mentorship.api.internal.mutations.program.Program")
@patch("apps.mentorship.api.internal.mutations.program.Mentor")
def test_update_program_status_success(
    MockMentor, MockProgram, mock_info, mock_program, mock_mentor
):
    """Test successful update of program status."""
    MockProgram.objects.get.return_value = mock_program
    MockMentor.objects.get.return_value = mock_mentor
    mock_program.admins.filter.return_value.exists.return_value = True

    input_data = MagicMock(key="program-key", status=ProgramStatusEnum.PUBLISHED)

    mutation = ProgramMutation()
    result = mutation.update_program_status(mock_info, input_data)

    MockProgram.objects.get.assert_called_once_with(key="program-key")
    MockMentor.objects.get.assert_called_once_with(nest_user=mock_info.context.request.user)
    mock_program.admins.filter.assert_called_once_with(id=mock_mentor.id)
    assert mock_program.status == ProgramStatusEnum.PUBLISHED.value
    mock_program.save.assert_called_once()
    assert result == mock_program


@patch("apps.mentorship.api.internal.mutations.program.Program")
def test_update_program_status_not_found(MockProgram, mock_info):
    """Test update_program_status fails if program is not found."""
    MockProgram.objects.get.side_effect = ObjectDoesNotExist

    input_data = MagicMock(key="nonexistent")
    mutation = ProgramMutation()
    with pytest.raises(ObjectDoesNotExist, match="Program with key 'nonexistent' not found."):
        mutation.update_program_status(mock_info, input_data)


@patch("apps.mentorship.api.internal.mutations.program.Program")
@patch("apps.mentorship.api.internal.mutations.program.Mentor")
def test_update_program_status_not_mentor(MockMentor, MockProgram, mock_info, mock_program):
    """Test update_program_status fails if user is not a mentor."""
    MockProgram.objects.get.return_value = mock_program
    MockMentor.objects.get.side_effect = ObjectDoesNotExist

    input_data = MagicMock(key="program-key")
    mutation = ProgramMutation()
    with pytest.raises(PermissionDenied, match="You must be a mentor to update a program."):
        mutation.update_program_status(mock_info, input_data)


@patch("apps.mentorship.api.internal.mutations.program.Program")
@patch("apps.mentorship.api.internal.mutations.program.Mentor")
def test_update_program_status_not_admin(
    MockMentor, MockProgram, mock_info, mock_program, mock_mentor
):
    """Test update_program_status fails if user is not a program admin."""
    MockProgram.objects.get.return_value = mock_program
    MockMentor.objects.get.return_value = mock_mentor
    mock_program.admins.filter.return_value.exists.return_value = False

    input_data = MagicMock(key="program-key")
    mutation = ProgramMutation()
    with pytest.raises(PermissionDenied):
        mutation.update_program_status(mock_info, input_data)
