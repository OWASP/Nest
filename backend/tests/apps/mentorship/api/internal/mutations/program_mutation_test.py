"""Tests for mentorship program mutations."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError

from apps.mentorship.api.internal.mutations.program import (
    ProgramMutation,
    resolve_admins_from_logins,
)
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


class TestResolveAdminsFromLogins:
    """Tests for resolve_admins_from_logins helper function."""

    @patch("apps.mentorship.api.internal.mutations.program.get_user_model")
    @patch("apps.mentorship.api.internal.mutations.program.Admin")
    @patch("apps.mentorship.api.internal.mutations.program.GithubUser")
    def test_resolve_success_with_nest_user(self, mock_gh, mock_admin, mock_get_user_model):
        """Test resolving logins when admin already has a nest_user."""
        mock_github_user = MagicMock()
        mock_gh.objects.get.return_value = mock_github_user

        mock_admin_obj = MagicMock()
        mock_admin_obj.nest_user = MagicMock()  # Already set
        mock_admin.objects.get_or_create.return_value = (mock_admin_obj, False)

        result = resolve_admins_from_logins(["admin1"])

        assert mock_admin_obj in result
        mock_admin_obj.save.assert_not_called()

    @patch("apps.mentorship.api.internal.mutations.program.get_user_model")
    @patch("apps.mentorship.api.internal.mutations.program.Admin")
    @patch("apps.mentorship.api.internal.mutations.program.GithubUser")
    def test_resolve_links_nest_user(self, mock_gh, mock_admin, mock_get_user_model):
        """Test resolving logins links nest_user when missing."""
        mock_user = mock_get_user_model.return_value
        mock_github_user = MagicMock()
        mock_gh.objects.get.return_value = mock_github_user

        mock_admin_obj = MagicMock()
        mock_admin_obj.nest_user = None
        mock_admin.objects.get_or_create.return_value = (mock_admin_obj, True)

        mock_nest_user = MagicMock()
        mock_user.objects.get.return_value = mock_nest_user

        result = resolve_admins_from_logins(["New_Admin"])

        assert mock_admin_obj in result
        assert mock_admin_obj.nest_user == mock_nest_user
        mock_admin_obj.save.assert_called_once_with(update_fields=["nest_user"])
        mock_gh.objects.get.assert_called_once_with(login__iexact="new_admin")

    @patch("apps.mentorship.api.internal.mutations.program.get_user_model")
    @patch("apps.mentorship.api.internal.mutations.program.Admin")
    @patch("apps.mentorship.api.internal.mutations.program.GithubUser")
    def test_resolve_nest_user_not_found(self, mock_gh, mock_admin, mock_get_user_model):
        """Test resolving logins when Nest user does not exist."""
        mock_user = mock_get_user_model.return_value
        mock_github_user = MagicMock(login="ghost")
        mock_gh.objects.get.return_value = mock_github_user

        mock_admin_obj = MagicMock()
        mock_admin_obj.nest_user = None
        mock_admin.objects.get_or_create.return_value = (mock_admin_obj, True)

        mock_user.DoesNotExist = type("DoesNotExist", (Exception,), {})
        mock_user.objects.get.side_effect = mock_user.DoesNotExist

        result = resolve_admins_from_logins(["ghost"])

        assert mock_admin_obj in result
        assert mock_admin_obj.nest_user is None

    @patch("apps.mentorship.api.internal.mutations.program.GithubUser")
    def test_resolve_github_user_not_found(self, mock_gh):
        """Test ValueError when GitHub user not found."""
        mock_gh.DoesNotExist = type("DoesNotExist", (Exception,), {})
        mock_gh.objects.get.side_effect = mock_gh.DoesNotExist

        with pytest.raises(ValueError, match="GitHub user 'unknown' not found"):
            resolve_admins_from_logins(["unknown"])

    def test_resolve_empty_logins(self):
        """Test resolving empty list returns empty set."""
        result = resolve_admins_from_logins([])
        assert result == set()


class TestCreateProgram:
    """Tests for ProgramMutation.create_program."""

    @patch("apps.mentorship.api.internal.mutations.program.ProgramAdmin")
    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Admin")
    def test_create_program_success(self, mock_admin, mock_program, mock_program_admin, mutation):
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

        mock_admin_obj = MagicMock()
        mock_admin.objects.get_or_create.return_value = (mock_admin_obj, False)

        mock_prog = MagicMock()
        mock_program.objects.create.return_value = mock_prog

        result = mutation.create_program(info, input_data)

        assert result == mock_prog
        mock_program.objects.create.assert_called_once()
        mock_program_admin.objects.create.assert_called_once()

    @patch("apps.mentorship.api.internal.mutations.program.ProgramAdmin")
    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Admin")
    def test_create_program_new_admin(
        self, mock_admin, mock_program, mock_program_admin, mutation
    ):
        """Test program creation with newly created admin profile."""
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

        mock_admin_obj = MagicMock()
        mock_admin.objects.get_or_create.return_value = (mock_admin_obj, True)
        mock_program.objects.create.return_value = MagicMock()

        result = mutation.create_program(info, input_data)
        assert result is not None

    @patch("apps.mentorship.api.internal.mutations.program.ProgramAdmin")
    @patch("apps.mentorship.api.internal.mutations.program.Program")
    @patch("apps.mentorship.api.internal.mutations.program.Admin")
    def test_create_program_sets_admin_nest_user(
        self, mock_admin, mock_program, mock_program_admin, mutation
    ):
        """Test create_program sets admin.nest_user when it is unset."""
        user = MagicMock()
        user.username = "testuser"
        info = _make_info(user)

        input_data = MagicMock()
        input_data.name = "Program"
        input_data.description = "Desc"
        input_data.mentees_limit = 5
        input_data.started_at = datetime(2025, 1, 1, tzinfo=UTC)
        input_data.ended_at = datetime(2025, 12, 31, tzinfo=UTC)
        input_data.domains = []
        input_data.tags = []

        mock_admin_obj = MagicMock()
        mock_admin_obj.nest_user = None  # No nest_user yet
        mock_admin.objects.get_or_create.return_value = (mock_admin_obj, True)
        mock_program.objects.create.return_value = MagicMock()

        mutation.create_program(info, input_data)

        assert mock_admin_obj.nest_user == user
        mock_admin_obj.save.assert_called_once_with(update_fields=["nest_user"])

    def test_create_program_end_before_start(self, mutation):
        """Test ValidationError when end date is before start date."""
        user = MagicMock()
        user.username = "testuser"
        info = _make_info(user)

        input_data = MagicMock()
        input_data.name = "Program"
        input_data.started_at = datetime(2025, 12, 31, tzinfo=UTC)
        input_data.ended_at = datetime(2025, 1, 1, tzinfo=UTC)

        with pytest.raises(ValidationError, match="End date must be after start date"):
            mutation.create_program(info, input_data)

    def test_create_program_end_equals_start(self, mutation):
        """Test ValidationError when end date equals start date."""
        user = MagicMock()
        user.username = "testuser"
        info = _make_info(user)

        input_data = MagicMock()
        input_data.name = "Program"
        same_date = datetime(2025, 6, 1, tzinfo=UTC)
        input_data.started_at = same_date
        input_data.ended_at = same_date

        with pytest.raises(ValidationError, match="End date must be after start date"):
            mutation.create_program(info, input_data)


class TestUpdateProgram:
    """Tests for ProgramMutation.update_program."""

    @patch("apps.mentorship.api.internal.mutations.program.resolve_admins_from_logins")
    @patch("apps.mentorship.api.internal.mutations.program.Program")
    def test_update_program_success(self, mock_program, mock_resolve, mutation):
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
    def test_update_program_not_admin(self, mock_program, mutation):
        """Test PermissionDenied when user is not an admin."""
        user = MagicMock()
        user.username = "testuser"
        info = _make_info(user)
        input_data = MagicMock()
        input_data.key = "prog-1"

        mock_prog = MagicMock()
        mock_prog.admins.filter.return_value.exists.return_value = False
        mock_program.objects.select_for_update.return_value.get.return_value = mock_prog

        with pytest.raises(
            PermissionDenied, match="You must be an admin of this program to update it"
        ):
            mutation.update_program(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    def test_update_program_invalid_dates(self, mock_program, mutation):
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

        with pytest.raises(ValidationError, match="End date must be after start date"):
            mutation.update_program(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    def test_update_program_with_none_dates(self, mock_program, mutation):
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

        result = mutation.update_program(info, input_data)

        assert result == mock_prog
        mock_prog.save.assert_called_once()
        mock_prog.admins.set.assert_not_called()

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    def test_update_program_with_status(self, mock_program, mutation):
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

        result = mutation.update_program(info, input_data)

        assert result == mock_prog
        assert mock_prog.status == ProgramStatusEnum.COMPLETED.value


class TestUpdateProgramStatus:
    """Tests for ProgramMutation.update_program_status."""

    @patch("apps.mentorship.api.internal.mutations.program.Program")
    def test_update_status_success(self, mock_program, mutation):
        """Test successful status update."""
        user = MagicMock()
        info = _make_info(user)

        input_data = MagicMock()
        input_data.key = "prog-1"
        input_data.status = ProgramStatusEnum.PUBLISHED

        mock_prog = MagicMock()
        mock_prog.admins.filter.return_value.exists.return_value = True
        mock_program.objects.select_for_update.return_value.get.return_value = mock_prog

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
    def test_update_status_not_admin(self, mock_program, mutation):
        """Test PermissionDenied when user is not an admin."""
        user = MagicMock()
        info = _make_info(user)
        input_data = MagicMock()
        input_data.key = "prog-1"

        mock_prog = MagicMock()
        mock_prog.admins.filter.return_value.exists.return_value = False
        mock_program.objects.select_for_update.return_value.get.return_value = mock_prog

        with pytest.raises(PermissionDenied):
            mutation.update_program_status(info, input_data)
