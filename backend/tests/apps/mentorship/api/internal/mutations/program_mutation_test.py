"""Tests for mentorship program mutations."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError

from apps.mentorship.api.internal.mutations.program import ProgramMutation
from apps.mentorship.api.internal.nodes.enum import ProgramStatusEnum


@pytest.fixture(autouse=True)
def _mock_transaction_atomic():
    """Disable transaction.atomic decorator for all tests."""
    with (
        patch("django.db.transaction.Atomic.__enter__", return_value=None),
        patch("django.db.transaction.Atomic.__exit__", return_value=False),
    ):
        yield


@pytest.fixture
def mutation():
    return ProgramMutation()


def _make_info(user):
    info = MagicMock()
    info.context.request.user = user
    return info


class TestCreateProgram:
    """Tests for ProgramMutation.create_program."""

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Mentor")
    def test_create_program_success(self, mock_mentor, mock_program, mutation):
        """Test successful program creation."""
        user = MagicMock()
        user.username = "testuser"
        info = _make_info(user)

        input_data = MagicMock()
        input_data.name = "Test Program"
        input_data.description = "Test"
        input_data.mentees_limit = 10
        input_data.started_at = datetime(2025, 1, 1, tzinfo=UTC)
        input_data.ended_at = datetime(2025, 12, 31, tzinfo=UTC)
        input_data.domains = []
        input_data.tags = []

        mock_mentor_obj = MagicMock()
        mock_mentor.objects.get_or_create.return_value = (mock_mentor_obj, False)

        mock_prog = MagicMock()
        mock_program.objects.create.return_value = mock_prog

        result = mutation.create_program(info, input_data)

        assert result == mock_prog
        mock_program.objects.create.assert_called_once()
        mock_prog.admins.set.assert_called_once_with([mock_mentor_obj])

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Mentor")
    def test_create_program_new_mentor(self, mock_mentor, mock_program, mutation):
        """Test program creation with newly created mentor profile."""
        user = MagicMock()
        user.username = "newuser"
        info = _make_info(user)

        input_data = MagicMock()
        input_data.name = "Program"
        input_data.description = "Desc"
        input_data.mentees_limit = 5
        input_data.started_at = datetime(2025, 1, 1, tzinfo=UTC)
        input_data.ended_at = datetime(2025, 12, 31, tzinfo=UTC)
        input_data.domains = []
        input_data.tags = []

        mock_mentor_obj = MagicMock()
        mock_mentor.objects.get_or_create.return_value = (mock_mentor_obj, True)
        mock_program.objects.create.return_value = MagicMock()

        result = mutation.create_program(info, input_data)
        assert result is not None

    @patch("apps.mentorship.api.internal.mutations.program.Mentor")
    def test_create_program_end_before_start(self, mock_mentor, mutation):
        """Test ValidationError when end date is before start date."""
        user = MagicMock()
        user.username = "testuser"
        info = _make_info(user)

        input_data = MagicMock()
        input_data.name = "Program"
        input_data.started_at = datetime(2025, 12, 31, tzinfo=UTC)
        input_data.ended_at = datetime(2025, 1, 1, tzinfo=UTC)

        mock_mentor.objects.get_or_create.return_value = (MagicMock(), False)

        with pytest.raises(ValidationError, match="End date must be after start date"):
            mutation.create_program(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.program.Mentor")
    def test_create_program_end_equals_start(self, mock_mentor, mutation):
        """Test ValidationError when end date equals start date."""
        user = MagicMock()
        user.username = "testuser"
        info = _make_info(user)

        input_data = MagicMock()
        input_data.name = "Program"
        same_date = datetime(2025, 6, 1, tzinfo=UTC)
        input_data.started_at = same_date
        input_data.ended_at = same_date

        mock_mentor.objects.get_or_create.return_value = (MagicMock(), False)

        with pytest.raises(ValidationError, match="End date must be after start date"):
            mutation.create_program(info, input_data)


class TestUpdateProgram:
    """Tests for ProgramMutation.update_program."""

    @patch("apps.mentorship.api.internal.mutations.program.resolve_mentors_from_logins")
    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Mentor")
    def test_update_program_success(
        self, mock_mentor, mock_program, mock_resolve, mutation
    ):
        """Test successful program update."""
        user = MagicMock()
        info = _make_info(user)

        input_data = MagicMock()
        input_data.key = "prog-1"
        input_data.name = "Updated"
        input_data.description = "Updated desc"
        input_data.mentees_limit = 20
        input_data.started_at = datetime(2025, 1, 1, tzinfo=UTC)
        input_data.ended_at = datetime(2025, 12, 31, tzinfo=UTC)
        input_data.domains = ["web"]
        input_data.tags = ["python"]
        input_data.status = ProgramStatusEnum.PUBLISHED
        input_data.admin_logins = ["admin1"]

        mock_prog = MagicMock()
        mock_prog.admins.filter.return_value.exists.return_value = True
        mock_program.objects.select_for_update.return_value.get.return_value = mock_prog
        mock_mentor.objects.get.return_value = MagicMock()
        mock_resolve.return_value = {MagicMock()}

        result = mutation.update_program(info, input_data)

        assert result == mock_prog
        mock_prog.save.assert_called_once()
        mock_prog.admins.set.assert_called_once()

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    def test_update_program_not_found(self, mock_program, mutation):
        """Test ObjectDoesNotExist when program not found."""
        user = MagicMock()
        info = _make_info(user)
        input_data = MagicMock()
        input_data.key = "bad"

        mock_program.DoesNotExist = type("DoesNotExist", (Exception,), {})
        mock_program.objects.select_for_update.return_value.get.side_effect = (
            mock_program.DoesNotExist
        )

        with pytest.raises(ObjectDoesNotExist, match="Program with key 'bad' not found"):
            mutation.update_program(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Mentor")
    def test_update_program_not_mentor(self, mock_mentor, mock_program, mutation):
        """Test PermissionDenied when user is not a mentor."""
        user = MagicMock()
        user.username = "testuser"
        info = _make_info(user)
        input_data = MagicMock()
        input_data.key = "prog-1"

        mock_program.objects.select_for_update.return_value.get.return_value = MagicMock()
        mock_mentor.DoesNotExist = type("DoesNotExist", (Exception,), {})
        mock_mentor.objects.get.side_effect = mock_mentor.DoesNotExist

        with pytest.raises(PermissionDenied, match="You must be a mentor to update a program"):
            mutation.update_program(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Mentor")
    def test_update_program_not_admin(self, mock_mentor, mock_program, mutation):
        """Test PermissionDenied when mentor is not admin."""
        user = MagicMock()
        user.username = "testuser"
        info = _make_info(user)
        input_data = MagicMock()
        input_data.key = "prog-1"

        mock_prog = MagicMock()
        mock_prog.admins.filter.return_value.exists.return_value = False
        mock_program.objects.select_for_update.return_value.get.return_value = mock_prog
        mock_mentor.objects.get.return_value = MagicMock()

        with pytest.raises(
            PermissionDenied, match="You must be an admin of this program to update it"
        ):
            mutation.update_program(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Mentor")
    def test_update_program_invalid_dates(self, mock_mentor, mock_program, mutation):
        """Test ValidationError when end date is before start date."""
        user = MagicMock()
        user.username = "testuser"
        info = _make_info(user)

        input_data = MagicMock()
        input_data.key = "prog-1"
        input_data.started_at = datetime(2025, 12, 31, tzinfo=UTC)
        input_data.ended_at = datetime(2025, 1, 1, tzinfo=UTC)

        mock_prog = MagicMock()
        mock_prog.admins.filter.return_value.exists.return_value = True
        mock_program.objects.select_for_update.return_value.get.return_value = mock_prog
        mock_mentor.objects.get.return_value = MagicMock()

        with pytest.raises(ValidationError, match="End date must be after start date"):
            mutation.update_program(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Mentor")
    def test_update_program_with_none_dates(self, mock_mentor, mock_program, mutation):
        """Test update succeeds when dates are None (no validation triggered)."""
        user = MagicMock()
        info = _make_info(user)

        input_data = MagicMock()
        input_data.key = "prog-1"
        input_data.name = "Updated"
        input_data.description = "Updated desc"
        input_data.mentees_limit = 10
        input_data.started_at = None
        input_data.ended_at = None
        input_data.domains = None
        input_data.tags = None
        input_data.status = None
        input_data.admin_logins = None

        mock_prog = MagicMock()
        mock_prog.admins.filter.return_value.exists.return_value = True
        mock_program.objects.select_for_update.return_value.get.return_value = mock_prog
        mock_mentor.objects.get.return_value = MagicMock()

        result = mutation.update_program(info, input_data)

        assert result == mock_prog
        mock_prog.save.assert_called_once()
        mock_prog.admins.set.assert_not_called()

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Mentor")
    def test_update_program_with_status(self, mock_mentor, mock_program, mutation):
        """Test update with status change."""
        user = MagicMock()
        info = _make_info(user)

        input_data = MagicMock()
        input_data.key = "prog-1"
        input_data.name = "Updated"
        input_data.description = "desc"
        input_data.mentees_limit = 10
        input_data.started_at = datetime(2025, 1, 1, tzinfo=UTC)
        input_data.ended_at = datetime(2025, 12, 31, tzinfo=UTC)
        input_data.domains = None
        input_data.tags = None
        input_data.status = ProgramStatusEnum.COMPLETED
        input_data.admin_logins = None

        mock_prog = MagicMock()
        mock_prog.admins.filter.return_value.exists.return_value = True
        mock_program.objects.select_for_update.return_value.get.return_value = mock_prog
        mock_mentor.objects.get.return_value = MagicMock()

        result = mutation.update_program(info, input_data)

        assert result == mock_prog
        assert mock_prog.status == ProgramStatusEnum.COMPLETED.value


class TestUpdateProgramStatus:
    """Tests for ProgramMutation.update_program_status."""

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Mentor")
    def test_update_status_success(self, mock_mentor, mock_program, mutation):
        """Test successful status update."""
        user = MagicMock()
        info = _make_info(user)

        input_data = MagicMock()
        input_data.key = "prog-1"
        input_data.status = ProgramStatusEnum.PUBLISHED

        mock_prog = MagicMock()
        mock_prog.admins.filter.return_value.exists.return_value = True
        mock_program.objects.select_for_update.return_value.get.return_value = mock_prog
        mock_mentor.objects.get.return_value = MagicMock()

        result = mutation.update_program_status(info, input_data)

        assert result == mock_prog
        assert mock_prog.status == ProgramStatusEnum.PUBLISHED.value
        mock_prog.save.assert_called_once()

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    def test_update_status_program_not_found(self, mock_program, mutation):
        """Test ObjectDoesNotExist when program not found."""
        user = MagicMock()
        info = _make_info(user)
        input_data = MagicMock()
        input_data.key = "bad"

        mock_program.DoesNotExist = type("DoesNotExist", (Exception,), {})
        mock_program.objects.select_for_update.return_value.get.side_effect = (
            mock_program.DoesNotExist
        )

        with pytest.raises(ObjectDoesNotExist, match="Program with key 'bad' not found"):
            mutation.update_program_status(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Mentor")
    def test_update_status_not_mentor(self, mock_mentor, mock_program, mutation):
        """Test PermissionDenied when user is not a mentor."""
        user = MagicMock()
        info = _make_info(user)
        input_data = MagicMock()
        input_data.key = "prog-1"

        mock_program.objects.select_for_update.return_value.get.return_value = MagicMock()
        mock_mentor.DoesNotExist = type("DoesNotExist", (Exception,), {})
        mock_mentor.objects.get.side_effect = mock_mentor.DoesNotExist

        with pytest.raises(PermissionDenied, match="You must be a mentor to update a program"):
            mutation.update_program_status(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Mentor")
    def test_update_status_not_admin(self, mock_mentor, mock_program, mutation):
        """Test PermissionDenied when mentor is not admin."""
        user = MagicMock()
        info = _make_info(user)
        input_data = MagicMock()
        input_data.key = "prog-1"

        mock_prog = MagicMock()
        mock_prog.admins.filter.return_value.exists.return_value = False
        mock_program.objects.select_for_update.return_value.get.return_value = mock_prog
        mock_mentor.objects.get.return_value = MagicMock()

        with pytest.raises(PermissionDenied):
            mutation.update_program_status(info, input_data)
