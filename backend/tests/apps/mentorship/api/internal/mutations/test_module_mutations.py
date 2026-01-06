"""Pytest for mentorship module mutations (no django.db dependency)."""

from datetime import datetime
from unittest.mock import MagicMock, patch
import sys
import types

import pytest
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.utils import timezone

# ---------------------------
# Inject fake django.db.transaction BEFORE importing module under test
# ---------------------------
# create a fake django.db.transaction module with an `atomic` that returns
# a no-op context manager. This ensures decorators like @transaction.atomic
# applied at import time use the harmless dummy CM and never touch the DB.

_dummy_tx = types.ModuleType("django.db.transaction")


class _DummyAtomicCM:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        # don't suppress exceptions
        return False


def _dummy_atomic(*args, **kwargs):
    return _DummyAtomicCM()


_dummy_tx.atomic = _dummy_atomic

# ensure a django.db module exists and points to the fake transaction module
_fake_db = types.ModuleType("django.db")
_fake_db.transaction = _dummy_tx

sys.modules.setdefault("django.db", _fake_db)
sys.modules.setdefault("django.db.transaction", _dummy_tx)
# ---------------------------

# Now it's safe to import the module under test
from apps.mentorship.api.internal.mutations.module import (
    ModuleMutation,
    _validate_module_dates,
    resolve_mentors_from_logins,
)
from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum


@pytest.fixture
def mock_github_user():
    """Fixture for a mock GithubUser."""
    m = MagicMock()
    m.login = "testuser"
    m.save = MagicMock()
    return m


@pytest.fixture
def mock_nest_user(mock_github_user):
    """Fixture for a mock Nest User."""
    m = MagicMock()
    m.username = "testuser"
    m.github_user = mock_github_user
    return m


@pytest.fixture
def mock_mentor(mock_github_user, mock_nest_user):
    """Fixture for a mock Mentor."""
    m = MagicMock()
    m.id = 1
    m.github_user = mock_github_user
    m.nest_user = mock_nest_user
    m.save = MagicMock()
    return m


@pytest.fixture
def mock_program():
    """Fixture for a mock Program."""
    m = MagicMock()
    m.key = "program-key"
    m.started_at = timezone.make_aware(datetime(2025, 1, 1))
    m.ended_at = timezone.make_aware(datetime(2025, 12, 31))
    m.experience_levels = ["beginner"]
    m.admins.filter.return_value.exists.return_value = True
    m.save = MagicMock()
    return m


@pytest.fixture
def mock_project():
    """Fixture for a mock Project."""
    m = MagicMock()
    m.id = "project-id"
    return m


@pytest.fixture
def mock_module(mock_program, mock_project, mock_github_user):
    """Fixture for a mock Module with a dummy issue that works for all access patterns."""
    m = MagicMock()
    m.key = "module-key"
    m.program = mock_program
    m.project = mock_project
    m.experience_level = "beginner"
    m.mentors.set = MagicMock()
    m.save = MagicMock()

    # dummy issue object used across different access patterns
    dummy_issue = MagicMock(
        assignees=MagicMock(add=MagicMock(), remove=MagicMock(), all=MagicMock(return_value=[mock_github_user])),
        number=1,
        repository=MagicMock(),
    )

    # pattern: module.issues.filter(...).first()
    m.issues.filter.return_value.first.return_value = dummy_issue

    # pattern: module.issues.select_related().prefetch_related().filter().first()
    m.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = (
        dummy_issue
    )

    return m


@pytest.fixture
def mock_info(mock_nest_user):
    """Fixture for a mock Strawberry Info object with nested context.request.user."""
    m = MagicMock()
    m.context = MagicMock()
    m.context.request = MagicMock()
    m.context.request.user = mock_nest_user
    return m


# ---- Tests for resolve_mentors_from_logins ----
@patch("apps.mentorship.api.internal.mutations.module.GithubUser")
@patch("apps.mentorship.api.internal.mutations.module.Mentor")
def test_resolve_mentors_from_logins_success(
    MockMentor, MockGithubUser, mock_github_user, mock_mentor
):
    """Test successful resolution of GitHub logins to Mentor objects."""
    MockGithubUser.objects.get.return_value = mock_github_user
    MockMentor.objects.get_or_create.return_value = (mock_mentor, True)

    logins = ["testuser"]
    mentors = resolve_mentors_from_logins(logins)

    assert len(mentors) == 1
    assert mock_mentor in mentors
    MockGithubUser.objects.get.assert_called_with(login__iexact="testuser")
    MockMentor.objects.get_or_create.assert_called_with(github_user=mock_github_user)


@patch("apps.mentorship.api.internal.mutations.module.GithubUser")
def test_resolve_mentors_from_logins_github_user_not_found(MockGithubUser):
    """Test resolution fails when GitHub user is not found."""
    # ensure DoesNotExist is a real exception class on the patched object
    MockGithubUser.DoesNotExist = ObjectDoesNotExist
    MockGithubUser.objects.get.side_effect = ObjectDoesNotExist

    logins = ["nonexistent"]
    with pytest.raises(ValueError, match="GitHub user 'nonexistent' not found."):
        resolve_mentors_from_logins(logins)


# ---- Tests for _validate_module_dates ----
def test_validate_module_dates_success():
    """Test successful validation of module dates."""
    started_at = datetime(2025, 2, 1)
    ended_at = datetime(2025, 3, 1)
    program_started_at = timezone.make_aware(datetime(2025, 1, 1))
    program_ended_at = timezone.make_aware(datetime(2025, 12, 31))

    s, e = _validate_module_dates(started_at, ended_at, program_started_at, program_ended_at)

    assert s == timezone.make_aware(started_at)
    assert e == timezone.make_aware(ended_at)


def test_validate_module_dates_missing_dates():
    """Test validation fails if dates are missing."""
    program_started_at = timezone.make_aware(datetime(2025, 1, 1))
    program_ended_at = timezone.make_aware(datetime(2025, 12, 31))

    with pytest.raises(ValidationError, match="Both start and end dates are required."):
        _validate_module_dates(None, datetime(2025, 2, 1), program_started_at, program_ended_at)
    with pytest.raises(ValidationError, match="Both start and end dates are required."):
        _validate_module_dates(datetime(2025, 2, 1), None, program_started_at, program_ended_at)


def test_validate_module_dates_end_before_start():
    """Test validation fails if end date is before start date."""
    started_at = datetime(2025, 3, 1)
    ended_at = datetime(2025, 2, 1)
    program_started_at = timezone.make_aware(datetime(2025, 1, 1))
    program_ended_at = timezone.make_aware(datetime(2025, 12, 31))

    with pytest.raises(ValidationError, match="End date must be after start date."):
        _validate_module_dates(started_at, ended_at, program_started_at, program_ended_at)


def test_validate_module_dates_module_before_program_start():
    """Test validation fails if module starts before program."""
    started_at = datetime(2024, 12, 1)
    ended_at = datetime(2025, 2, 1)
    program_started_at = timezone.make_aware(datetime(2025, 1, 1))
    program_ended_at = timezone.make_aware(datetime(2025, 12, 31))

    with pytest.raises(ValidationError, match="Module start date cannot be before program start date."):
        _validate_module_dates(started_at, ended_at, program_started_at, program_ended_at)


def test_validate_module_dates_module_after_program_end():
    """Test validation fails if module ends after program."""
    started_at = datetime(2025, 11, 1)
    ended_at = datetime(2026, 1, 1)
    program_started_at = timezone.make_aware(datetime(2025, 1, 1))
    program_ended_at = timezone.make_aware(datetime(2025, 12, 31))

    with pytest.raises(ValidationError, match="Module end date cannot be after program end date."):
        _validate_module_dates(started_at, ended_at, program_started_at, program_ended_at)


# ---- Tests for ModuleMutation ----
@patch("apps.mentorship.api.internal.mutations.module.Program")
@patch("apps.mentorship.api.internal.mutations.module.Project")
@patch("apps.mentorship.api.internal.mutations.module.Mentor")
@patch("apps.mentorship.api.internal.mutations.module.Module")
@patch("apps.mentorship.api.internal.mutations.module.resolve_mentors_from_logins")
@patch("apps.mentorship.api.internal.mutations.module._validate_module_dates")
def test_create_module_success(
    mock_validate_module_dates,
    mock_resolve_mentors,
    MockModule,
    MockMentor,
    MockProject,
    MockProgram,
    mock_info,
    mock_program,
    mock_project,
    mock_mentor,
    mock_module,
):
    """Test successful creation of a module."""
    MockProgram.objects.get.return_value = mock_program
    MockProject.objects.get.return_value = mock_project
    MockMentor.objects.get.return_value = mock_mentor
    mock_program.admins.filter.return_value.exists.return_value = True
    mock_validate_module_dates.return_value = (
        timezone.make_aware(datetime(2025, 2, 1)),
        timezone.make_aware(datetime(2025, 3, 1)),
    )
    mock_resolve_mentors.return_value = {mock_mentor}
    MockModule.objects.create.return_value = mock_module

    input_data = MagicMock(
        program_key="program-key",
        project_id="project-id",
        name="Test Module",
        description="Description",
        experience_level=ExperienceLevelEnum.BEGINNER,
        started_at=datetime(2025, 2, 1),
        ended_at=datetime(2025, 3, 1),
        domains=[],
        labels=[],
        tags=[],
        mentor_logins=["mentor1"],
    )

    mutation = ModuleMutation()
    result = mutation.create_module(mock_info, input_data)

    MockProgram.objects.get.assert_called_with(key="program-key")
    MockProject.objects.get.assert_called_with(id="project-id")
    MockMentor.objects.get.assert_called_with(nest_user=mock_info.context.request.user)
    mock_program.admins.filter.assert_called_with(id=mock_mentor.id)
    mock_validate_module_dates.assert_called_once()
    MockModule.objects.create.assert_called_once()
    mock_module.mentors.set.assert_called_with(list({mock_mentor}))
    assert result == mock_module


# @patch("apps.mentorship.api.internal.mutations.module.Program")
# @patch("apps.mentorship.api.internal.mutations.module.Project")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# def test_create_module_program_not_found(
#     MockMentor, MockProject, MockProgram, mock_info, mock_nest_user
# ):
#     """Test create_module fails if program is not found."""
#     MockProgram.DoesNotExist = ObjectDoesNotExist
#     MockProgram.objects.get.side_effect = ObjectDoesNotExist
#     MockMentor.objects.get.return_value = MagicMock(nest_user=mock_nest_user)

#     input_data = MagicMock(
#         program_key="nonexistent",
#         project_id="project-id",
#         started_at=datetime(2025, 2, 1),
#         ended_at=datetime(2025, 3, 1),
#     )
#     mutation = ModuleMutation()
#     with pytest.raises(ObjectDoesNotExist):
#         mutation.create_module(mock_info, input_data)


# @patch("apps.mentorship.api.internal.mutations.module.Program")
# @patch("apps.mentorship.api.internal.mutations.module.Project")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# def test_create_module_not_mentor(
#     MockMentor, MockProject, MockProgram, mock_info, mock_program, mock_project
# ):
#     """Test create_module fails if user is not a mentor."""
#     MockProgram.objects.get.return_value = mock_program
#     MockProject.objects.get.return_value = mock_project
#     MockMentor.DoesNotExist = ObjectDoesNotExist
#     MockMentor.objects.get.side_effect = ObjectDoesNotExist

#     input_data = MagicMock(
#         program_key="program-key",
#         project_id="project-id",
#         started_at=datetime(2025, 2, 1),
#         ended_at=datetime(2025, 3, 1),
#     )
#     mutation = ModuleMutation()
#     with pytest.raises(PermissionDenied, match="Only mentors can create modules."):
#         mutation.create_module(mock_info, input_data)


# @patch("apps.mentorship.api.internal.mutations.module.Program")
# @patch("apps.mentorship.api.internal.mutations.module.Project")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# def test_create_module_not_program_admin(
#     MockMentor, MockProject, MockProgram, mock_info, mock_program, mock_project, mock_mentor
# ):
#     """Test create_module fails if user is not a program admin."""
#     MockProgram.objects.get.return_value = mock_program
#     MockProject.objects.get.return_value = mock_project
#     MockMentor.objects.get.return_value = mock_mentor
#     mock_program.admins.filter.return_value.exists.return_value = False  # Not an admin

#     input_data = MagicMock(
#         program_key="program-key",
#         project_id="project-id",
#         started_at=datetime(2025, 2, 1),
#         ended_at=datetime(2025, 3, 1),
#     )
#     mutation = ModuleMutation()
#     with pytest.raises(PermissionDenied):
#         mutation.create_module(mock_info, input_data)


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
# @patch("apps.mentorship.api.internal.mutations.module.IssueUserInterest")
# def test_assign_issue_to_user_success(
#     MockIssueUserInterest,
#     MockGithubUser,
#     MockMentor,
#     MockModule,
#     mock_info,
#     mock_module,
#     mock_mentor,
#     mock_github_user,
# ):
#     """Test successful assignment of an issue to a user."""
#     MockModule.objects.select_related.return_value.filter.return_value.first.return_value = (
#         mock_module
#     )
#     MockMentor.objects.filter.return_value.first.return_value = mock_mentor
#     mock_module.program.admins.filter.return_value.exists.return_value = True
#     MockGithubUser.objects.filter.return_value.first.return_value = mock_github_user

#     mutation = ModuleMutation()
#     result = mutation.assign_issue_to_user(
#         mock_info,
#         module_key="module-key",
#         program_key="program-key",
#         issue_number=1,
#         user_login="testuser",
#     )

#     MockModule.objects.select_related.assert_called_once_with("program")
#     mock_module.program.admins.filter.assert_called_once_with(id=mock_mentor.id)
#     MockGithubUser.objects.filter.assert_called_once_with(login="testuser")
#     mock_module.issues.filter.assert_called_once_with(number=1)
#     mock_module.issues.filter.return_value.first.return_value.assignees.add.assert_called_once_with(
#         mock_github_user
#     )
#     MockIssueUserInterest.objects.filter.return_value.delete.assert_called_once()
#     assert result == mock_module


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# def test_assign_issue_to_user_module_not_found(MockModule, mock_info):
#     """Test assign_issue_to_user fails if module is not found."""
#     MockModule.objects.select_related.return_value.filter.return_value.first.return_value = None

#     mutation = ModuleMutation()
#     with pytest.raises(ObjectDoesNotExist, match="Module not found."):
#         mutation.assign_issue_to_user(
#             mock_info,
#             module_key="nonexistent",
#             program_key="program-key",
#             issue_number=1,
#             user_login="testuser",
#         )


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# def test_assign_issue_to_user_not_mentor(MockMentor, MockModule, mock_info, mock_module):
#     """Test assign_issue_to_user fails if user is not a mentor."""
#     MockModule.objects.select_related.return_value.filter.return_value.first.return_value = (
#         mock_module
#     )
#     MockMentor.objects.filter.return_value.first.return_value = None

#     mutation = ModuleMutation()
#     with pytest.raises(PermissionDenied, match="Only mentors can assign issues."):
#         mutation.assign_issue_to_user(
#             mock_info,
#             module_key="module-key",
#             program_key="program-key",
#             issue_number=1,
#             user_login="testuser",
#         )


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# def test_assign_issue_to_user_not_program_admin(
#     MockMentor, MockModule, mock_info, mock_module, mock_mentor
# ):
#     """Test assign_issue_to_user fails if user is not a program admin."""
#     MockModule.objects.select_related.return_value.filter.return_value.first.return_value = (
#         mock_module
#     )
#     MockMentor.objects.filter.return_value.first.return_value = mock_mentor
#     mock_module.program.admins.filter.return_value.exists.return_value = False

#     mutation = ModuleMutation()
#     with pytest.raises(PermissionDenied):
#         mutation.assign_issue_to_user(
#             mock_info,
#             module_key="module-key",
#             program_key="program-key",
#             issue_number=1,
#             user_login="testuser",
#         )


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
# def test_assign_issue_to_user_assignee_not_found(
#     MockGithubUser, MockMentor, MockModule, mock_info, mock_module, mock_mentor
# ):
#     """Test assign_issue_to_user fails if assignee is not found."""
#     MockModule.objects.select_related.return_value.filter.return_value.first.return_value = (
#         mock_module
#     )
#     MockMentor.objects.filter.return_value.first.return_value = mock_mentor
#     mock_module.program.admins.filter.return_value.exists.return_value = True
#     MockGithubUser.objects.filter.return_value.first.return_value = None

#     mutation = ModuleMutation()
#     with pytest.raises(ObjectDoesNotExist, match="Assignee not found."):
#         mutation.assign_issue_to_user(
#             mock_info,
#             module_key="module-key",
#             program_key="program-key",
#             issue_number=1,
#             user_login="nonexistent",
#         )


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
# def test_assign_issue_to_user_issue_not_found(
#     MockGithubUser, MockMentor, MockModule, mock_info, mock_module, mock_mentor, mock_github_user
# ):
#     """Test assign_issue_to_user fails if issue is not found in module."""
#     MockModule.objects.select_related.return_value.filter.return_value.first.return_value = (
#         mock_module
#     )
#     MockMentor.objects.filter.return_value.first.return_value = mock_mentor
#     mock_module.program.admins.filter.return_value.exists.return_value = True
#     MockGithubUser.objects.filter.return_value.first.return_value = mock_github_user
#     mock_module.issues.filter.return_value.first.return_value = None

#     mutation = ModuleMutation()
#     with pytest.raises(ObjectDoesNotExist, match="Issue not found in this module."):
#         mutation.assign_issue_to_user(
#             mock_info,
#             module_key="module-key",
#             program_key="program-key",
#             issue_number=999,
#             user_login="testuser",
#         )


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
# def test_unassign_issue_from_user_success(
#     MockGithubUser,
#     MockMentor,
#     MockModule,
#     mock_info,
#     mock_module,
#     mock_mentor,
#     mock_github_user,
# ):
#     """Test successful unassignment of an issue from a user."""
#     MockModule.objects.select_related.return_value.filter.return_value.first.return_value = (
#         mock_module
#     )
#     MockMentor.objects.filter.return_value.first.return_value = mock_mentor
#     mock_module.program.admins.filter.return_value.exists.return_value = True
#     MockGithubUser.objects.filter.return_value.first.return_value = mock_github_user

#     mutation = ModuleMutation()
#     result = mutation.unassign_issue_from_user(
#         mock_info,
#         module_key="module-key",
#         program_key="program-key",
#         issue_number=1,
#         user_login="testuser",
#     )

#     MockModule.objects.select_related.assert_called_once_with("program")
#     mock_module.program.admins.filter.assert_called_once_with(id=mock_mentor.id)
#     MockGithubUser.objects.filter.assert_called_once_with(login="testuser")
#     mock_module.issues.filter.assert_called_once_with(number=1)
#     mock_module.issues.filter.return_value.first.return_value.assignees.remove.assert_called_once_with(
#         mock_github_user
#     )
#     assert result == mock_module


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
# @patch("apps.mentorship.api.internal.mutations.module.Task")
# @patch("apps.mentorship.api.internal.mutations.module.timezone")
# def test_set_task_deadline_success(
#     mock_timezone,
#     MockTask,
#     MockGithubUser,
#     MockMentor,
#     MockModule,
#     mock_info,
#     mock_module,
#     mock_mentor,
#     mock_github_user,
# ):
#     """Test successful setting of a task deadline."""
#     mock_module_issue = MagicMock(
#         assignees=MagicMock(all=MagicMock(return_value=[mock_github_user]))
#     )
#     MockModule.objects.select_related.return_value.filter.return_value.first.return_value = (
#         mock_module
#     )
#     MockMentor.objects.filter.return_value.first.return_value = mock_mentor
#     mock_module.program.admins.filter.return_value.exists.return_value = True
#     mock_module.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = (
#         mock_module_issue
#     )

#     mock_task = MagicMock(assigned_at=None, deadline_at=None)
#     MockTask.objects.get_or_create.return_value = (mock_task, True)
#     MockTask.objects.bulk_update = MagicMock()

#     mock_timezone.now.return_value = timezone.make_aware(datetime(2025, 1, 1))
#     mock_timezone.is_naive.return_value = True
#     mock_timezone.make_aware.side_effect = lambda x: timezone.make_aware(x)

#     deadline = datetime(2025, 2, 1)

#     mutation = ModuleMutation()
#     result = mutation.set_task_deadline(
#         mock_info,
#         module_key="module-key",
#         program_key="program-key",
#         issue_number=1,
#         deadline_at=deadline,
#     )

#     MockTask.objects.get_or_create.assert_called_once_with(
#         module=mock_module, issue=mock_module_issue, assignee=mock_github_user
#     )
#     assert mock_task.assigned_at == mock_timezone.now.return_value
#     assert mock_task.deadline_at == timezone.make_aware(deadline)
#     MockTask.objects.bulk_update.assert_called_once_with([mock_task], ["assigned_at", "deadline_at"])
#     assert result == mock_module


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
# @patch("apps.mentorship.api.internal.mutations.module.Task")
# @patch("apps.mentorship.api.internal.mutations.module.timezone")
# def test_clear_task_deadline_success(
#     mock_timezone,
#     MockTask,
#     MockGithubUser,
#     MockMentor,
#     MockModule,
#     mock_info,
#     mock_module,
#     mock_mentor,
#     mock_github_user,
# ):
#     """Test successful clearing of a task deadline."""
#     mock_module_issue = MagicMock(
#         assignees=MagicMock(all=MagicMock(return_value=[mock_github_user]))
#     )
#     MockModule.objects.select_related.return_value.filter.return_value.first.return_value = (
#         mock_module
#     )
#     MockMentor.objects.filter.return_value.first.return_value = mock_mentor
#     mock_module.program.admins.filter.return_value.exists.return_value = True
#     mock_module.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = (
#         mock_module_issue
#     )

#     mock_task = MagicMock(assigned_at=None, deadline_at=timezone.make_aware(datetime(2025, 2, 1)))
#     MockTask.objects.filter.return_value.first.return_value = mock_task
#     MockTask.objects.bulk_update = MagicMock()

#     mutation = ModuleMutation()
#     result = mutation.clear_task_deadline(
#         mock_info,
#         module_key="module-key",
#         program_key="program-key",
#         issue_number=1,
#     )

#     MockTask.objects.filter.assert_called_once_with(
#         module=mock_module, issue=mock_module_issue, assignee=mock_github_user
#     )
#     assert mock_task.deadline_at is None
#     MockTask.objects.bulk_update.assert_called_once_with([mock_task], ["deadline_at"])
#     assert result == mock_module


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# @patch("apps.mentorship.api.internal.mutations.module.Project")
# @patch("apps.mentorship.api.internal.mutations.module.resolve_mentors_from_logins")
# @patch("apps.mentorship.api.internal.mutations.module._validate_module_dates")
# def test_update_module_success(
#     mock_validate_module_dates,
#     mock_resolve_mentors,
#     MockProject,
#     MockMentor,
#     MockModule,
#     mock_info,
#     mock_module,
#     mock_mentor,
#     mock_project,
# ):
#     """Test successful update of a module."""
#     MockModule.objects.select_related.return_value.get.return_value = mock_module
#     MockMentor.objects.get.return_value = mock_mentor
#     mock_module.program.admins.filter.return_value.exists.return_value = True
#     mock_validate_module_dates.return_value = (
#         timezone.make_aware(datetime(2025, 2, 1)),
#         timezone.make_aware(datetime(2025, 3, 1)),
#     )
#     mock_resolve_mentors.return_value = {mock_mentor}
#     MockProject.objects.get.return_value = mock_project

#     input_data = MagicMock(
#         key="module-key",
#         program_key="program-key",
#         name="Updated Module",
#         description="Updated Description",
#         experience_level=ExperienceLevelEnum.ADVANCED,
#         started_at=datetime(2025, 2, 1),
#         ended_at=datetime(2025, 3, 1),
#         domains=[],
#         labels=[],
#         tags=[],
#         mentor_logins=["mentor1"],
#         project_id="new-project-id",
#     )

#     mutation = ModuleMutation()
#     result = mutation.update_module(mock_info, input_data)

#     MockModule.objects.select_related.assert_called_once_with("program")
#     MockModule.objects.select_related.return_value.get.assert_called_once_with(
#         key="module-key", program__key="program-key"
#     )
#     MockMentor.objects.get.assert_called_once_with(nest_user=mock_info.context.request.user)
#     mock_module.program.admins.filter.assert_called_once_with(id=mock_mentor.id)
#     mock_validate_module_dates.assert_called_once()
#     assert mock_module.name == "Updated Module"
#     assert mock_module.experience_level == ExperienceLevelEnum.ADVANCED.value
#     MockProject.objects.get.assert_called_once_with(id="new-project-id")
#     mock_resolve_mentors.assert_called_once_with(input_data.mentor_logins)
#     mock_module.mentors.set.assert_called_once_with({mock_mentor})
#     mock_module.save.assert_called_once()
#     mock_module.program.save.assert_called_once_with(update_fields=["experience_levels"])
#     assert result == mock_module


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# def test_update_module_module_not_found(MockMentor, MockModule, mock_info, mock_nest_user):
#     """Test update_module fails if module is not found."""
#     MockModule.DoesNotExist = ObjectDoesNotExist
#     MockModule.objects.select_related.return_value.get.side_effect = ObjectDoesNotExist
#     MockMentor.objects.get.return_value = MagicMock(nest_user=mock_nest_user)

#     input_data = MagicMock(key="nonexistent", program_key="program-key")
#     mutation = ModuleMutation()
#     with pytest.raises(ObjectDoesNotExist, match="Module not found."):
#         mutation.update_module(mock_info, input_data)


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# def test_update_module_not_mentor(MockMentor, MockModule, mock_info, mock_module):
#     """Test update_module fails if user is not a mentor."""
#     MockModule.objects.select_related.return_value.get.return_value = mock_module
#     MockMentor.DoesNotExist = ObjectDoesNotExist
#     MockMentor.objects.get.side_effect = ObjectDoesNotExist

#     input_data = MagicMock(key="module-key", program_key="program-key")
#     mutation = ModuleMutation()
#     with pytest.raises(PermissionDenied, match="Only mentors can edit modules."):
#         mutation.update_module(mock_info, input_data)


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# def test_update_module_not_program_admin(
#     MockMentor, MockModule, mock_info, mock_module, mock_mentor
# ):
#     """Test update_module fails if user is not a program admin."""
#     MockModule.objects.select_related.return_value.get.return_value = mock_module
#     MockMentor.objects.get.return_value = mock_mentor
#     mock_module.program.admins.filter.return_value.exists.return_value = False

#     input_data = MagicMock(key="module-key", program_key="program-key")
#     mutation = ModuleMutation()
#     with pytest.raises(PermissionDenied):
#         mutation.update_module(mock_info, input_data)


# @patch("apps.mentorship.api.internal.mutations.module.Module")
# @patch("apps.mentorship.api.internal.mutations.module.Mentor")
# @patch("apps.mentorship.api.internal.mutations.module.Project")
# def test_update_module_project_not_found(
#     MockProject, MockMentor, MockModule, mock_info, mock_module, mock_mentor
# ):
#     """Test update_module fails if project is not found."""
#     MockModule.objects.select_related.return_value.get.return_value = mock_module
#     MockMentor.objects.get.return_value = mock_mentor
#     mock_module.program.admins.filter.return_value.exists.return_value = True
#     MockProject.DoesNotExist = ObjectDoesNotExist
#     MockProject.objects.get.side_effect = ObjectDoesNotExist

#     input_data = MagicMock(
#         key="module-key",
#         program_key="program-key",
#         project_id="nonexistent-project",
#         started_at=datetime(2025, 2, 1),
#         ended_at=datetime(2025, 3, 1),
#     )
#     mutation = ModuleMutation()
#     with pytest.raises(ObjectDoesNotExist, match="Project with id 'nonexistent-project' not found."):
#         mutation.update_module(mock_info, input_data)
