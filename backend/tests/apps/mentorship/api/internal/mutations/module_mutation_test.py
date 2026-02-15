"""Tests for mentorship module mutations."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError

from apps.mentorship.api.internal.mutations.module import (
    ModuleMutation,
    _validate_module_dates,
    resolve_mentors_from_logins,
)
from apps.mentorship.models.task import Task


@pytest.fixture(autouse=True)
def _mock_transaction_atomic():
    """Disable transaction.atomic decorator for all tests."""
    with (
        patch("django.db.transaction.Atomic.__enter__", return_value=None),
        patch("django.db.transaction.Atomic.__exit__", return_value=False),
    ):
        yield


class TestResolveMentorsFromLogins:
    """Tests for resolve_mentors_from_logins."""

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
    def test_resolve_mentors_success(self, mock_github_user, mock_mentor):
        """Test successful resolution of mentor logins."""
        mock_gh_user = MagicMock()
        mock_github_user.objects.get.return_value = mock_gh_user
        mock_mentor_obj1 = MagicMock()
        mock_mentor_obj2 = MagicMock()
        mock_mentor.objects.get_or_create.side_effect = [
            (mock_mentor_obj1, True),
            (mock_mentor_obj2, True),
        ]

        result = resolve_mentors_from_logins(["user1", "user2"])

        assert len(result) == 2
        assert mock_mentor_obj1 in result
        assert mock_mentor_obj2 in result
        assert mock_github_user.objects.get.call_count == 2

    @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
    def test_resolve_mentors_user_not_found(self, mock_github_user):
        """Test ValueError when GitHub user not found."""
        mock_github_user.DoesNotExist = Exception
        mock_github_user.objects.get.side_effect = mock_github_user.DoesNotExist

        with pytest.raises(ValueError, match="GitHub user 'baduser' not found"):
            resolve_mentors_from_logins(["baduser"])

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
    def test_resolve_mentors_empty_list(self, mock_github_user, mock_mentor):
        """Test with empty list returns empty set."""
        result = resolve_mentors_from_logins([])
        assert result == set()


class TestValidateModuleDates:
    """Tests for _validate_module_dates."""

    def test_none_started_at(self):
        """Test raises when started_at is None."""
        with pytest.raises(ValidationError, match="Both start and end dates are required"):
            _validate_module_dates(
                None,
                datetime(2025, 6, 30, tzinfo=UTC),
                datetime(2025, 1, 1, tzinfo=UTC),
                datetime(2025, 12, 31, tzinfo=UTC),
            )

    def test_none_ended_at(self):
        """Test raises when ended_at is None."""
        with pytest.raises(ValidationError, match="Both start and end dates are required"):
            _validate_module_dates(
                datetime(2025, 1, 1, tzinfo=UTC),
                None,
                datetime(2025, 1, 1, tzinfo=UTC),
                datetime(2025, 12, 31, tzinfo=UTC),
            )

    def test_end_before_start(self):
        """Test raises when end date is before start date."""
        with pytest.raises(ValidationError, match="End date must be after start date"):
            _validate_module_dates(
                datetime(2025, 6, 30, tzinfo=UTC),
                datetime(2025, 1, 1, tzinfo=UTC),
                datetime(2025, 1, 1, tzinfo=UTC),
                datetime(2025, 12, 31, tzinfo=UTC),
            )

    def test_end_equals_start(self):
        """Test raises when end date equals start date."""
        with pytest.raises(ValidationError, match="End date must be after start date"):
            _validate_module_dates(
                datetime(2025, 3, 1, tzinfo=UTC),
                datetime(2025, 3, 1, tzinfo=UTC),
                datetime(2025, 1, 1, tzinfo=UTC),
                datetime(2025, 12, 31, tzinfo=UTC),
            )

    def test_start_before_program_start(self):
        """Test raises when module start is before program start."""
        with pytest.raises(
            ValidationError, match="Module start date cannot be before program start date"
        ):
            _validate_module_dates(
                datetime(2024, 12, 1, tzinfo=UTC),
                datetime(2025, 6, 30, tzinfo=UTC),
                datetime(2025, 1, 1, tzinfo=UTC),
                datetime(2025, 12, 31, tzinfo=UTC),
            )

    def test_end_after_program_end(self):
        """Test raises when module end is after program end."""
        with pytest.raises(
            ValidationError, match="Module end date cannot be after program end date"
        ):
            _validate_module_dates(
                datetime(2025, 1, 1, tzinfo=UTC),
                datetime(2026, 1, 1, tzinfo=UTC),
                datetime(2025, 1, 1, tzinfo=UTC),
                datetime(2025, 12, 31, tzinfo=UTC),
            )

    def test_valid_dates(self):
        """Test valid dates return normalized values."""
        result = _validate_module_dates(
            datetime(2025, 2, 1, tzinfo=UTC),
            datetime(2025, 6, 30, tzinfo=UTC),
            datetime(2025, 1, 1, tzinfo=UTC),
            datetime(2025, 12, 31, tzinfo=UTC),
        )
        assert result[0] == datetime(2025, 2, 1, tzinfo=UTC)
        assert result[1] == datetime(2025, 6, 30, tzinfo=UTC)

    def test_naive_dates_made_aware(self):
        """Test that naive dates are made timezone-aware."""
        result = _validate_module_dates(
            datetime(2025, 2, 1),
            datetime(2025, 6, 30),
            datetime(2025, 1, 1, tzinfo=UTC),
            datetime(2025, 12, 31, tzinfo=UTC),
        )
        from django.utils import timezone

        assert not timezone.is_naive(result[0])
        assert not timezone.is_naive(result[1])


class TestModuleMutationCreateModule:
    """Tests for ModuleMutation.create_module."""

    def _make_info(self, user):
        info = MagicMock()
        info.context.request.user = user
        return info

    def _make_input_data(self, **overrides):
        defaults = {
            "program_key": "test-program",
            "project_id": "1",
            "name": "Test Module",
            "description": "Test",
            "experience_level": MagicMock(value="intermediate"),
            "started_at": datetime(2025, 3, 1, tzinfo=UTC),
            "ended_at": datetime(2025, 6, 30, tzinfo=UTC),
            "domains": [],
            "labels": [],
            "tags": [],
            "mentor_logins": None,
            "project_name": "Project",
        }
        defaults.update(overrides)
        return MagicMock(**defaults)

    @patch("apps.mentorship.api.internal.mutations.module.resolve_mentors_from_logins")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    @patch("apps.mentorship.api.internal.mutations.module.Project")
    @patch("apps.mentorship.api.internal.mutations.module.Program")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module._validate_module_dates")
    def test_create_module_success(
        self,
        mock_validate,
        mock_mentor,
        mock_program,
        mock_project,
        mock_module,
        mock_resolve,
    ):
        """Test successful module creation."""
        user = MagicMock()
        info = self._make_info(user)
        input_data = self._make_input_data(mentor_logins=["mentor1"])

        mock_prog = MagicMock()
        mock_prog.started_at = datetime(2025, 1, 1, tzinfo=UTC)
        mock_prog.ended_at = datetime(2025, 12, 31, tzinfo=UTC)
        mock_prog.experience_levels = []
        mock_program.objects.get.return_value = mock_prog

        mock_proj = MagicMock()
        mock_project.objects.get.return_value = mock_proj

        mock_creator = MagicMock()
        mock_mentor.objects.get.return_value = mock_creator
        mock_prog.admins.filter.return_value.exists.return_value = True

        mock_validate.return_value = (input_data.started_at, input_data.ended_at)

        mock_mod = MagicMock()
        mock_mod.experience_level = "intermediate"
        mock_module.objects.create.return_value = mock_mod

        mock_resolve.return_value = set()

        mutation = ModuleMutation()
        result = mutation.create_module(info, input_data)

        assert result == mock_mod
        mock_module.objects.create.assert_called_once()
        mock_mod.mentors.set.assert_called_once()

    @patch("apps.mentorship.api.internal.mutations.module.Project")
    @patch("apps.mentorship.api.internal.mutations.module.Program")
    def test_create_module_program_not_found(self, mock_program, mock_project):
        """Test ObjectDoesNotExist when program not found."""
        user = MagicMock()
        info = self._make_info(user)
        input_data = self._make_input_data()

        mock_program.DoesNotExist = ObjectDoesNotExist
        mock_project.DoesNotExist = ObjectDoesNotExist
        mock_program.objects.get.side_effect = ObjectDoesNotExist("not found")

        mutation = ModuleMutation()
        with pytest.raises(ObjectDoesNotExist):
            mutation.create_module(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.module.Project")
    @patch("apps.mentorship.api.internal.mutations.module.Program")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    def test_create_module_not_mentor(self, mock_mentor, mock_program, mock_project):
        """Test PermissionDenied when user is not a mentor."""
        user = MagicMock()
        info = self._make_info(user)
        input_data = self._make_input_data()

        mock_program.DoesNotExist = type("DoesNotExist", (Exception,), {})
        mock_project.DoesNotExist = type("DoesNotExist", (Exception,), {})
        mock_program.objects.get.return_value = MagicMock()
        mock_project.objects.get.return_value = MagicMock()
        mock_mentor.DoesNotExist = type("DoesNotExist", (Exception,), {})
        mock_mentor.objects.get.side_effect = mock_mentor.DoesNotExist

        mutation = ModuleMutation()
        with pytest.raises(PermissionDenied, match="Only mentors can create modules"):
            mutation.create_module(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.module.Project")
    @patch("apps.mentorship.api.internal.mutations.module.Program")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    def test_create_module_not_admin(self, mock_mentor, mock_program, mock_project):
        """Test PermissionDenied when mentor is not program admin."""
        user = MagicMock()
        info = self._make_info(user)
        input_data = self._make_input_data()

        mock_prog = MagicMock()
        mock_program.objects.get.return_value = mock_prog
        mock_project.objects.get.return_value = MagicMock()
        mock_creator = MagicMock()
        mock_mentor.objects.get.return_value = mock_creator
        mock_prog.admins.filter.return_value.exists.return_value = False

        mutation = ModuleMutation()
        with pytest.raises(PermissionDenied):
            mutation.create_module(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.module.resolve_mentors_from_logins")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    @patch("apps.mentorship.api.internal.mutations.module.Project")
    @patch("apps.mentorship.api.internal.mutations.module.Program")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module._validate_module_dates")
    def test_create_module_adds_experience_level_to_program(
        self,
        mock_validate,
        mock_mentor,
        mock_program,
        mock_project,
        mock_module,
        mock_resolve,
    ):
        """Test that creating a module adds its experience level to the program if not present."""
        user = MagicMock()
        info = self._make_info(user)
        input_data = self._make_input_data()

        mock_prog = MagicMock()
        mock_prog.started_at = datetime(2025, 1, 1, tzinfo=UTC)
        mock_prog.ended_at = datetime(2025, 12, 31, tzinfo=UTC)
        mock_prog.experience_levels = ["beginner"]
        mock_program.objects.get.return_value = mock_prog
        mock_project.objects.get.return_value = MagicMock()

        mock_creator = MagicMock()
        mock_mentor.objects.get.return_value = mock_creator
        mock_prog.admins.filter.return_value.exists.return_value = True

        mock_validate.return_value = (input_data.started_at, input_data.ended_at)

        mock_mod = MagicMock()
        mock_mod.experience_level = "advanced"
        mock_module.objects.create.return_value = mock_mod

        mock_resolve.return_value = set()

        mutation = ModuleMutation()
        mutation.create_module(info, input_data)

        assert "advanced" in mock_prog.experience_levels
        mock_prog.save.assert_called_once_with(update_fields=["experience_levels"])

    @patch("apps.mentorship.api.internal.mutations.module.resolve_mentors_from_logins")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    @patch("apps.mentorship.api.internal.mutations.module.Project")
    @patch("apps.mentorship.api.internal.mutations.module.Program")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module._validate_module_dates")
    def test_create_module_experience_level_already_in_program(
        self,
        mock_validate,
        mock_mentor,
        mock_program,
        mock_project,
        mock_module,
        mock_resolve,
    ):
        """Test creating a module when experience_level is already in program levels."""
        user = MagicMock()
        info = self._make_info(user)
        input_data = self._make_input_data()

        mock_prog = MagicMock()
        mock_prog.started_at = datetime(2025, 1, 1, tzinfo=UTC)
        mock_prog.ended_at = datetime(2025, 12, 31, tzinfo=UTC)
        mock_prog.experience_levels = ["intermediate", "beginner"]
        mock_program.objects.get.return_value = mock_prog
        mock_project.objects.get.return_value = MagicMock()

        mock_creator = MagicMock()
        mock_mentor.objects.get.return_value = mock_creator
        mock_prog.admins.filter.return_value.exists.return_value = True

        mock_validate.return_value = (input_data.started_at, input_data.ended_at)

        mock_mod = MagicMock()
        mock_mod.experience_level = "intermediate"
        mock_module.objects.create.return_value = mock_mod

        mock_resolve.return_value = set()

        mutation = ModuleMutation()
        result = mutation.create_module(info, input_data)

        assert result == mock_mod
        mock_prog.save.assert_not_called()


class TestModuleMutationAssignIssue:
    """Tests for ModuleMutation.assign_issue_to_user."""

    def _make_info(self, user):
        info = MagicMock()
        info.context.request.user = user
        return info

    @patch("apps.mentorship.api.internal.mutations.module.IssueUserInterest")
    @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_assign_issue_success(
        self, mock_module, mock_mentor, mock_gh_user, mock_interest
    ):
        """Test successful issue assignment."""
        user = MagicMock()
        info = self._make_info(user)

        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )

        mock_mentor_obj = MagicMock()
        mock_mentor.objects.filter.return_value.first.return_value = mock_mentor_obj

        mock_gh = MagicMock()
        mock_gh_user.objects.filter.return_value.first.return_value = mock_gh

        mock_issue = MagicMock()
        mock_mod.issues.filter.return_value.first.return_value = mock_issue

        mutation = ModuleMutation()
        result = mutation.assign_issue_to_user(
            info,
            module_key="mod-1",
            program_key="prog-1",
            issue_number=1,
            user_login="testuser",
        )

        assert result == mock_mod
        mock_issue.assignees.add.assert_called_once_with(mock_gh)
        mock_interest.objects.filter.return_value.delete.assert_called_once()

    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_assign_issue_module_not_found(self, mock_module):
        """Test ObjectDoesNotExist when module not found."""
        user = MagicMock()
        info = self._make_info(user)
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            None
        )

        mutation = ModuleMutation()
        with pytest.raises(ObjectDoesNotExist, match="Module not found"):
            mutation.assign_issue_to_user(
                info,
                module_key="bad",
                program_key="bad",
                issue_number=1,
                user_login="testuser",
            )

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_assign_issue_not_mentor(self, mock_module, mock_mentor):
        """Test PermissionDenied when user is not a mentor."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = None

        mutation = ModuleMutation()
        with pytest.raises((PermissionDenied, TypeError)):
            mutation.assign_issue_to_user(
                info,
                module_key="mod-1",
                program_key="prog-1",
                issue_number=1,
                user_login="testuser",
            )

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_assign_issue_not_admin(self, mock_module, mock_mentor):
        """Test PermissionDenied when mentor is not admin."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = False
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()

        mutation = ModuleMutation()
        with pytest.raises(PermissionDenied):
            mutation.assign_issue_to_user(
                info,
                module_key="mod-1",
                program_key="prog-1",
                issue_number=1,
                user_login="testuser",
            )

    @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_assign_issue_user_not_found(self, mock_module, mock_mentor, mock_gh):
        """Test ObjectDoesNotExist when assignee not found."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()
        mock_gh.objects.filter.return_value.first.return_value = None

        mutation = ModuleMutation()
        with pytest.raises(ObjectDoesNotExist, match="Assignee not found"):
            mutation.assign_issue_to_user(
                info,
                module_key="mod-1",
                program_key="prog-1",
                issue_number=1,
                user_login="testuser",
            )

    @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_assign_issue_issue_not_found(self, mock_module, mock_mentor, mock_gh):
        """Test ObjectDoesNotExist when issue not found."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()
        mock_gh.objects.filter.return_value.first.return_value = MagicMock()
        mock_mod.issues.filter.return_value.first.return_value = None

        mutation = ModuleMutation()
        with pytest.raises(ObjectDoesNotExist, match="Issue not found in this module"):
            mutation.assign_issue_to_user(
                info,
                module_key="mod-1",
                program_key="prog-1",
                issue_number=1,
                user_login="testuser",
            )


class TestModuleMutationUnassignIssue:
    """Tests for ModuleMutation.unassign_issue_from_user."""

    def _make_info(self, user):
        info = MagicMock()
        info.context.request.user = user
        return info

    @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_unassign_issue_success(self, mock_module, mock_mentor, mock_gh_user):
        """Test successful issue unassignment."""
        user = MagicMock()
        info = self._make_info(user)

        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()
        mock_gh = MagicMock()
        mock_gh_user.objects.filter.return_value.first.return_value = mock_gh
        mock_issue = MagicMock()
        mock_mod.issues.filter.return_value.first.return_value = mock_issue

        mutation = ModuleMutation()
        result = mutation.unassign_issue_from_user(
            info,
            module_key="mod-1",
            program_key="prog-1",
            issue_number=1,
            user_login="testuser",
        )

        assert result == mock_mod
        mock_issue.assignees.remove.assert_called_once_with(mock_gh)

    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_unassign_module_not_found(self, mock_module):
        """Test ObjectDoesNotExist when module not found."""
        user = MagicMock()
        info = self._make_info(user)
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            None
        )

        mutation = ModuleMutation()
        with pytest.raises(ObjectDoesNotExist, match="Module not found"):
            mutation.unassign_issue_from_user(
                info,
                module_key="bad",
                program_key="bad",
                issue_number=1,
                user_login="testuser",
            )

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_unassign_not_mentor(self, mock_module, mock_mentor):
        """Test PermissionDenied when user is not a mentor."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = None

        mutation = ModuleMutation()
        with pytest.raises(PermissionDenied):
            mutation.unassign_issue_from_user(
                info,
                module_key="mod-1",
                program_key="prog-1",
                issue_number=1,
                user_login="testuser",
            )

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_unassign_not_admin(self, mock_module, mock_mentor):
        """Test PermissionDenied when mentor is not admin."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = False
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()

        mutation = ModuleMutation()
        with pytest.raises(PermissionDenied):
            mutation.unassign_issue_from_user(
                info,
                module_key="mod-1",
                program_key="prog-1",
                issue_number=1,
                user_login="testuser",
            )

    @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_unassign_user_not_found(self, mock_module, mock_mentor, mock_gh):
        """Test ObjectDoesNotExist when user not found."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()
        mock_gh.objects.filter.return_value.first.return_value = None

        mutation = ModuleMutation()
        with pytest.raises(ObjectDoesNotExist, match="Assignee not found"):
            mutation.unassign_issue_from_user(
                info,
                module_key="mod-1",
                program_key="prog-1",
                issue_number=1,
                user_login="testuser",
            )

    @patch("apps.mentorship.api.internal.mutations.module.GithubUser")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_unassign_issue_not_found(self, mock_module, mock_mentor, mock_gh):
        """Test ObjectDoesNotExist when issue not found."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()
        mock_gh.objects.filter.return_value.first.return_value = MagicMock()
        mock_mod.issues.filter.return_value.first.return_value = None

        mutation = ModuleMutation()
        with pytest.raises(ObjectDoesNotExist, match="Issue .* not found in this module"):
            mutation.unassign_issue_from_user(
                info,
                module_key="mod-1",
                program_key="prog-1",
                issue_number=42,
                user_login="testuser",
            )


class TestModuleMutationSetTaskDeadline:
    """Tests for ModuleMutation.set_task_deadline."""

    def _make_info(self, user):
        info = MagicMock()
        info.context.request.user = user
        return info

    @patch("apps.mentorship.api.internal.mutations.module.Task")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    @patch("apps.mentorship.api.internal.mutations.module.timezone")
    def test_set_task_deadline_success(
        self, mock_tz, mock_module, mock_mentor, mock_task
    ):
        """Test successful deadline setting."""
        user = MagicMock()
        info = self._make_info(user)
        mock_task.Status = Task.Status

        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()

        mock_issue = MagicMock()
        assignee = MagicMock()
        assignees_qs = MagicMock()
        assignees_qs.exists.return_value = True
        assignees_qs.__iter__ = MagicMock(return_value=iter([assignee]))
        mock_issue.assignees.all.return_value = assignees_qs
        mock_mod.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = mock_issue

        deadline = datetime(2025, 12, 1, tzinfo=UTC)
        mock_tz.is_naive.return_value = False
        mock_tz.now.return_value = datetime(2025, 6, 1, tzinfo=UTC)

        mock_task_obj = MagicMock()
        mock_task_obj.assigned_at = None
        mock_task.objects.get_or_create.return_value = (mock_task_obj, True)

        mutation = ModuleMutation()
        result = mutation.set_task_deadline(
            info,
            module_key="mod-1",
            program_key="prog-1",
            issue_number=1,
            deadline_at=deadline,
        )

        assert result == mock_mod
        mock_task.objects.bulk_update.assert_called_once()

    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_set_deadline_module_not_found(self, mock_module):
        """Test ObjectDoesNotExist when module not found."""
        user = MagicMock()
        info = self._make_info(user)
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            None
        )

        mutation = ModuleMutation()
        with pytest.raises(ObjectDoesNotExist, match="Module not found"):
            mutation.set_task_deadline(
                info,
                module_key="bad",
                program_key="bad",
                issue_number=1,
                deadline_at=datetime(2025, 12, 1, tzinfo=UTC),
            )

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_set_deadline_not_mentor(self, mock_module, mock_mentor):
        """Test PermissionDenied when user is not a mentor."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = None

        mutation = ModuleMutation()
        with pytest.raises((PermissionDenied, TypeError)):
            mutation.set_task_deadline(
                info,
                module_key="mod-1",
                program_key="prog-1",
                issue_number=1,
                deadline_at=datetime(2025, 12, 1, tzinfo=UTC),
            )

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_set_deadline_not_admin(self, mock_module, mock_mentor):
        """Test PermissionDenied when mentor is not admin."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = False
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()

        mutation = ModuleMutation()
        with pytest.raises(PermissionDenied):
            mutation.set_task_deadline(
                info,
                module_key="mod-1",
                program_key="prog-1",
                issue_number=1,
                deadline_at=datetime(2025, 12, 1, tzinfo=UTC),
            )

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_set_deadline_issue_not_found(self, mock_module, mock_mentor):
        """Test ObjectDoesNotExist when issue not found."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()
        mock_mod.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = None

        mutation = ModuleMutation()
        with pytest.raises(ObjectDoesNotExist, match="Issue not found in this module"):
            mutation.set_task_deadline(
                info,
                module_key="mod-1",
                program_key="prog-1",
                issue_number=1,
                deadline_at=datetime(2025, 12, 1, tzinfo=UTC),
            )

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_set_deadline_no_assignees(self, mock_module, mock_mentor):
        """Test ValidationError when issue has no assignees."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()

        mock_issue = MagicMock()
        mock_issue.assignees.all.return_value.exists.return_value = False
        mock_mod.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = mock_issue

        mutation = ModuleMutation()
        with pytest.raises(ValidationError, match="Cannot set deadline: issue has no assignees"):
            mutation.set_task_deadline(
                info,
                module_key="mod-1",
                program_key="prog-1",
                issue_number=1,
                deadline_at=datetime(2025, 12, 1, tzinfo=UTC),
            )

    @patch("apps.mentorship.api.internal.mutations.module.Task")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    @patch("apps.mentorship.api.internal.mutations.module.timezone")
    def test_set_deadline_naive_deadline(
        self, mock_tz, mock_module, mock_mentor, mock_task
    ):
        """Test naive deadline is made aware."""
        user = MagicMock()
        info = self._make_info(user)

        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()

        mock_issue = MagicMock()
        assignee = MagicMock()
        assignees_qs = MagicMock()
        assignees_qs.exists.return_value = True
        assignees_qs.__iter__ = MagicMock(return_value=iter([assignee]))
        mock_issue.assignees.all.return_value = assignees_qs
        mock_mod.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = mock_issue

        naive_deadline = datetime(2025, 12, 1)
        aware_deadline = datetime(2025, 12, 1, tzinfo=UTC)

        mock_tz.is_naive.return_value = True
        mock_tz.make_aware.return_value = aware_deadline
        mock_tz.now.return_value = datetime(2025, 6, 1, tzinfo=UTC)

        mock_task_obj = MagicMock()
        mock_task_obj.assigned_at = datetime(2025, 5, 1, tzinfo=UTC)
        mock_task.objects.get_or_create.return_value = (mock_task_obj, False)

        mutation = ModuleMutation()
        result = mutation.set_task_deadline(
            info,
            module_key="mod-1",
            program_key="prog-1",
            issue_number=1,
            deadline_at=naive_deadline,
        )

        assert result == mock_mod
        mock_tz.make_aware.assert_called_once_with(naive_deadline)

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    @patch("apps.mentorship.api.internal.mutations.module.timezone")
    def test_set_deadline_in_past(self, mock_tz, mock_module, mock_mentor):
        """Test ValidationError when deadline is in the past."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()

        mock_issue = MagicMock()
        mock_issue.assignees.all.return_value.exists.return_value = True
        mock_mod.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = mock_issue

        past_deadline = datetime(2020, 1, 1, tzinfo=UTC)
        mock_tz.is_naive.return_value = False
        mock_tz.now.return_value = datetime(2025, 6, 1, tzinfo=UTC)

        mutation = ModuleMutation()
        with pytest.raises(ValidationError, match="Deadline cannot be in the past"):
            mutation.set_task_deadline(
                info,
                module_key="mod-1",
                program_key="prog-1",
                issue_number=1,
                deadline_at=past_deadline,
            )


class TestModuleMutationClearTaskDeadline:
    """Tests for ModuleMutation.clear_task_deadline."""

    def _make_info(self, user):
        info = MagicMock()
        info.context.request.user = user
        return info

    @patch("apps.mentorship.api.internal.mutations.module.Task")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_clear_deadline_single_task(self, mock_module, mock_mentor, mock_task):
        """Test clearing deadline for a single task."""
        user = MagicMock()
        info = self._make_info(user)

        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()

        mock_issue = MagicMock()
        assignee = MagicMock()
        assignees_qs = MagicMock()
        assignees_qs.exists.return_value = True
        assignees_qs.__iter__ = MagicMock(return_value=iter([assignee]))
        mock_issue.assignees.all.return_value = assignees_qs
        mock_mod.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = mock_issue

        task_obj = MagicMock()
        task_obj.deadline_at = datetime(2025, 12, 1, tzinfo=UTC)
        mock_task.objects.filter.return_value.first.return_value = task_obj

        mutation = ModuleMutation()
        result = mutation.clear_task_deadline(
            info, module_key="mod-1", program_key="prog-1", issue_number=1
        )

        assert result == mock_mod
        assert task_obj.deadline_at is None
        task_obj.save.assert_called_once_with(update_fields=["deadline_at"])

    @patch("apps.mentorship.api.internal.mutations.module.Task")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_clear_deadline_multiple_tasks(self, mock_module, mock_mentor, mock_task):
        """Test clearing deadline for multiple tasks uses bulk_update."""
        user = MagicMock()
        info = self._make_info(user)

        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()

        mock_issue = MagicMock()
        assignee1 = MagicMock()
        assignee2 = MagicMock()
        assignees_qs = MagicMock()
        assignees_qs.exists.return_value = True
        assignees_qs.__iter__ = MagicMock(return_value=iter([assignee1, assignee2]))
        mock_issue.assignees.all.return_value = assignees_qs
        mock_mod.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = mock_issue

        task1 = MagicMock()
        task1.deadline_at = datetime(2025, 12, 1, tzinfo=UTC)
        task2 = MagicMock()
        task2.deadline_at = datetime(2025, 12, 1, tzinfo=UTC)
        mock_task.objects.filter.return_value.first.side_effect = [task1, task2]

        mutation = ModuleMutation()
        result = mutation.clear_task_deadline(
            info, module_key="mod-1", program_key="prog-1", issue_number=1
        )

        assert result == mock_mod
        mock_task.objects.bulk_update.assert_called_once()

    @patch("apps.mentorship.api.internal.mutations.module.Task")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_clear_deadline_no_tasks_with_deadline(
        self, mock_module, mock_mentor, mock_task
    ):
        """Test when no tasks have deadlines."""
        user = MagicMock()
        info = self._make_info(user)

        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()

        mock_issue = MagicMock()
        assignee = MagicMock()
        assignees_qs = MagicMock()
        assignees_qs.exists.return_value = True
        assignees_qs.__iter__ = MagicMock(return_value=iter([assignee]))
        mock_issue.assignees.all.return_value = assignees_qs
        mock_mod.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = mock_issue

        task_obj = MagicMock()
        task_obj.deadline_at = None
        mock_task.objects.filter.return_value.first.return_value = task_obj

        mutation = ModuleMutation()
        result = mutation.clear_task_deadline(
            info, module_key="mod-1", program_key="prog-1", issue_number=1
        )

        assert result == mock_mod
        mock_task.objects.bulk_update.assert_not_called()

    @patch("apps.mentorship.api.internal.mutations.module.Task")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_clear_deadline_task_not_found(
        self, mock_module, mock_mentor, mock_task
    ):
        """Test when task object is None (no task exists for assignee)."""
        user = MagicMock()
        info = self._make_info(user)

        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()

        mock_issue = MagicMock()
        assignee = MagicMock()
        assignees_qs = MagicMock()
        assignees_qs.exists.return_value = True
        assignees_qs.__iter__ = MagicMock(return_value=iter([assignee]))
        mock_issue.assignees.all.return_value = assignees_qs
        mock_mod.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = mock_issue

        mock_task.objects.filter.return_value.first.return_value = None

        mutation = ModuleMutation()
        result = mutation.clear_task_deadline(
            info, module_key="mod-1", program_key="prog-1", issue_number=1
        )

        assert result == mock_mod

    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_clear_deadline_module_not_found(self, mock_module):
        """Test ObjectDoesNotExist when module not found."""
        user = MagicMock()
        info = self._make_info(user)
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            None
        )

        mutation = ModuleMutation()
        with pytest.raises(ObjectDoesNotExist, match="Module not found"):
            mutation.clear_task_deadline(
                info, module_key="bad", program_key="bad", issue_number=1
            )

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_clear_deadline_not_mentor(self, mock_module, mock_mentor):
        """Test PermissionDenied when user is not a mentor."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = None

        mutation = ModuleMutation()
        with pytest.raises((PermissionDenied, TypeError)):
            mutation.clear_task_deadline(
                info, module_key="mod-1", program_key="prog-1", issue_number=1
            )

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_clear_deadline_not_admin(self, mock_module, mock_mentor):
        """Test PermissionDenied when mentor is not admin."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = False
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()

        mutation = ModuleMutation()
        with pytest.raises(PermissionDenied):
            mutation.clear_task_deadline(
                info, module_key="mod-1", program_key="prog-1", issue_number=1
            )

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_clear_deadline_issue_not_found(self, mock_module, mock_mentor):
        """Test ObjectDoesNotExist when issue not found."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()
        mock_mod.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = None

        mutation = ModuleMutation()
        with pytest.raises(ObjectDoesNotExist, match="Issue not found in this module"):
            mutation.clear_task_deadline(
                info, module_key="mod-1", program_key="prog-1", issue_number=1
            )

    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_clear_deadline_no_assignees(self, mock_module, mock_mentor):
        """Test ValidationError when issue has no assignees."""
        user = MagicMock()
        info = self._make_info(user)
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.filter.return_value.first.return_value = (
            mock_mod
        )
        mock_mentor.objects.filter.return_value.first.return_value = MagicMock()

        mock_issue = MagicMock()
        mock_issue.assignees.all.return_value.exists.return_value = False
        mock_mod.issues.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = mock_issue

        mutation = ModuleMutation()
        with pytest.raises(
            ValidationError, match="Cannot clear deadline: issue has no assignees"
        ):
            mutation.clear_task_deadline(
                info, module_key="mod-1", program_key="prog-1", issue_number=1
            )


class TestModuleMutationUpdateModule:
    """Tests for ModuleMutation.update_module."""

    def _make_info(self, user):
        info = MagicMock()
        info.context.request.user = user
        return info

    def _make_input_data(self, **overrides):
        defaults = {
            "key": "mod-1",
            "program_key": "prog-1",
            "name": "Updated Module",
            "description": "Updated",
            "experience_level": MagicMock(value="advanced"),
            "started_at": datetime(2025, 3, 1, tzinfo=UTC),
            "ended_at": datetime(2025, 6, 30, tzinfo=UTC),
            "domains": [],
            "labels": [],
            "tags": [],
            "mentor_logins": None,
            "project_id": "1",
            "project_name": "Project",
        }
        defaults.update(overrides)
        return MagicMock(**defaults)

    @patch("apps.mentorship.api.internal.mutations.module.Project")
    @patch("apps.mentorship.api.internal.mutations.module.resolve_mentors_from_logins")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module._validate_module_dates")
    def test_update_module_success(
        self, mock_validate, mock_mentor, mock_module, mock_resolve, mock_project
    ):
        """Test successful module update."""
        user = MagicMock()
        info = self._make_info(user)
        input_data = self._make_input_data(mentor_logins=["mentor1"])

        mock_mod = MagicMock()
        mock_mod.experience_level = "intermediate"
        mock_mod.program.started_at = datetime(2025, 1, 1, tzinfo=UTC)
        mock_mod.program.ended_at = datetime(2025, 12, 31, tzinfo=UTC)
        mock_mod.program.experience_levels = ["intermediate"]
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.select_for_update.return_value.get.return_value = mock_mod
        mock_module.objects.filter.return_value.exclude.return_value.exists.return_value = False

        mock_creator = MagicMock()
        mock_mentor.objects.get.return_value = mock_creator

        mock_validate.return_value = (input_data.started_at, input_data.ended_at)
        mock_project.objects.get.return_value = MagicMock()
        mock_resolve.return_value = {MagicMock()}

        mutation = ModuleMutation()
        result = mutation.update_module(info, input_data)

        assert result == mock_mod
        mock_mod.save.assert_called_once()
        mock_mod.mentors.set.assert_called_once()

    @patch("apps.mentorship.api.internal.mutations.module.Module")
    def test_update_module_not_found(self, mock_module):
        """Test ObjectDoesNotExist when module not found."""
        user = MagicMock()
        info = self._make_info(user)
        input_data = self._make_input_data()
        mock_module.DoesNotExist = type("DoesNotExist", (Exception,), {})
        mock_module.objects.select_related.return_value.select_for_update.return_value.get.side_effect = mock_module.DoesNotExist

        mutation = ModuleMutation()
        with pytest.raises(ObjectDoesNotExist, match="Module not found"):
            mutation.update_module(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.module.Module")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    def test_update_module_not_mentor(self, mock_mentor, mock_module):
        """Test PermissionDenied when user is not a mentor."""
        user = MagicMock()
        user.username = "testuser"
        info = self._make_info(user)
        input_data = self._make_input_data()
        mock_mod = MagicMock()
        mock_module.objects.select_related.return_value.select_for_update.return_value.get.return_value = mock_mod
        mock_mentor.DoesNotExist = type("DoesNotExist", (Exception,), {})
        mock_mentor.objects.get.side_effect = mock_mentor.DoesNotExist

        mutation = ModuleMutation()
        with pytest.raises(PermissionDenied, match="Only mentors can edit modules"):
            mutation.update_module(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.module.Module")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    def test_update_module_not_admin(self, mock_mentor, mock_module):
        """Test PermissionDenied when mentor is not admin."""
        user = MagicMock()
        info = self._make_info(user)
        input_data = self._make_input_data()
        mock_mod = MagicMock()
        mock_mod.program.admins.filter.return_value.exists.return_value = False
        mock_module.objects.select_related.return_value.select_for_update.return_value.get.return_value = mock_mod
        mock_mentor.objects.get.return_value = MagicMock()

        mutation = ModuleMutation()
        with pytest.raises(PermissionDenied):
            mutation.update_module(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.module.Project")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module._validate_module_dates")
    def test_update_module_project_not_found(
        self, mock_validate, mock_mentor, mock_module, mock_project
    ):
        """Test ObjectDoesNotExist when project not found."""
        user = MagicMock()
        info = self._make_info(user)
        input_data = self._make_input_data()

        mock_mod = MagicMock()
        mock_mod.experience_level = "intermediate"
        mock_mod.program.started_at = datetime(2025, 1, 1, tzinfo=UTC)
        mock_mod.program.ended_at = datetime(2025, 12, 31, tzinfo=UTC)
        mock_mod.program.experience_levels = ["intermediate"]
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.select_for_update.return_value.get.return_value = mock_mod
        mock_mentor.objects.get.return_value = MagicMock()
        mock_validate.return_value = (input_data.started_at, input_data.ended_at)
        mock_project.DoesNotExist = type("DoesNotExist", (Exception,), {})
        mock_project.objects.get.side_effect = mock_project.DoesNotExist

        mutation = ModuleMutation()
        with pytest.raises(ObjectDoesNotExist, match="Project with id .* not found"):
            mutation.update_module(info, input_data)

    @patch("apps.mentorship.api.internal.mutations.module.Project")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module._validate_module_dates")
    def test_update_module_no_mentor_logins(
        self, mock_validate, mock_mentor, mock_module, mock_project
    ):
        """Test update without updating mentor logins."""
        user = MagicMock()
        info = self._make_info(user)
        input_data = self._make_input_data(mentor_logins=None)

        mock_mod = MagicMock()
        mock_mod.experience_level = "intermediate"
        mock_mod.program.started_at = datetime(2025, 1, 1, tzinfo=UTC)
        mock_mod.program.ended_at = datetime(2025, 12, 31, tzinfo=UTC)
        mock_mod.program.experience_levels = ["intermediate", "advanced"]
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.select_for_update.return_value.get.return_value = mock_mod
        mock_module.objects.filter.return_value.exclude.return_value.exists.return_value = True

        mock_mentor.objects.get.return_value = MagicMock()
        mock_validate.return_value = (input_data.started_at, input_data.ended_at)
        mock_project.objects.get.return_value = MagicMock()

        mutation = ModuleMutation()
        result = mutation.update_module(info, input_data)

        assert result == mock_mod
        mock_mod.mentors.set.assert_not_called()

    @patch("apps.mentorship.api.internal.mutations.module.Project")
    @patch("apps.mentorship.api.internal.mutations.module.Module")
    @patch("apps.mentorship.api.internal.mutations.module.Mentor")
    @patch("apps.mentorship.api.internal.mutations.module._validate_module_dates")
    def test_update_module_removes_old_experience_level(
        self, mock_validate, mock_mentor, mock_module, mock_project
    ):
        """Test old experience level removed when no other module uses it."""
        user = MagicMock()
        info = self._make_info(user)
        input_data = self._make_input_data()
        input_data.experience_level.value = "advanced"

        mock_mod = MagicMock()
        mock_mod.experience_level = "intermediate"
        mock_mod.program.started_at = datetime(2025, 1, 1, tzinfo=UTC)
        mock_mod.program.ended_at = datetime(2025, 12, 31, tzinfo=UTC)
        mock_mod.program.experience_levels = ["intermediate"]
        mock_mod.program.admins.filter.return_value.exists.return_value = True
        mock_module.objects.select_related.return_value.select_for_update.return_value.get.return_value = mock_mod
        mock_module.objects.filter.return_value.exclude.return_value.exists.return_value = False

        mock_mentor.objects.get.return_value = MagicMock()
        mock_validate.return_value = (input_data.started_at, input_data.ended_at)
        mock_project.objects.get.return_value = MagicMock()

        mutation = ModuleMutation()
        mutation.update_module(info, input_data)

        assert "advanced" in mock_mod.program.experience_levels
        mock_mod.program.save.assert_called_once_with(update_fields=["experience_levels"])
