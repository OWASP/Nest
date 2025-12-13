"""Tests for the nest_update_badges management command."""

from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command

from apps.nest.management.commands.nest_update_badges import (
    OWASP_STAFF_BADGE_NAME,
    PROJECT_LEADER_BADGE_NAME,
)


def make_mock_employees(mock_employee):
    mock_employees = MagicMock()
    mock_employees_without_badge = MagicMock()
    # This makes iterating over employees_without_badge yield mock_employee (not a list)
    mock_employees_without_badge.__iter__.return_value = iter([mock_employee])
    mock_employees_without_badge.count.return_value = 1
    mock_employees_without_badge.values_list.return_value = [mock_employee.id]
    mock_employees_without_badge.distinct.return_value = mock_employees_without_badge
    mock_employees.exclude.return_value = mock_employees_without_badge
    return mock_employees, mock_employees_without_badge


def make_mock_former_employees(mock_former_employee):
    mock_former_employees = MagicMock()
    mock_former_employees.__iter__.return_value = iter([mock_former_employee])
    mock_former_employees.count.return_value = 1
    mock_former_employees.values_list.return_value = [mock_former_employee.id]
    mock_former_employees.distinct.return_value = mock_former_employees
    return mock_former_employees


def extract_is_owasp_staff(arg):
    """Extract is_owasp_staff value from Q object, dict, or tuple."""
    if hasattr(arg, "children"):
        for key, value in arg.children:
            if key == "is_owasp_staff":
                return value
    if isinstance(arg, dict) and "is_owasp_staff" in arg:
        return arg["is_owasp_staff"]
    if isinstance(arg, tuple) and len(arg) == 2 and arg[0] == "is_owasp_staff":
        return arg[1]
    return None


def user_filter_side_effect_factory(mock_employees, mock_former_employees):
    """Create a side effect function for User.objects.filter."""

    def get_mock_for_staff_value(value):
        if value is True:
            return mock_employees
        if value is False:
            return mock_former_employees
        return None

    def user_filter_side_effect(*args, **kwargs):
        staff_value = kwargs.get("is_owasp_staff")
        if staff_value is not None:
            return get_mock_for_staff_value(staff_value)
        for arg in args:
            staff_value = extract_is_owasp_staff(arg)
            result = get_mock_for_staff_value(staff_value)
            if result:
                return result
        return MagicMock()

    return user_filter_side_effect


class TestSyncUserBadgesCommand:
    """Tests for the nest_update_badges management command."""

    @patch("apps.nest.management.commands.nest_update_badges.UserBadge.objects.get_or_create")
    @patch("apps.nest.management.commands.nest_update_badges.UserBadge.objects.filter")
    @patch("apps.nest.management.commands.nest_update_badges.Badge.objects.get_or_create")
    @patch("apps.nest.management.commands.nest_update_badges.User.objects.filter")
    def test_sync_owasp_staff_badge(
        self,
        mock_user_filter,
        mock_badge_get_or_create,
        mock_user_badge_filter,
        mock_user_badge_get_or_create,
    ):
        # Set up badge mock
        mock_badge = MagicMock()
        mock_badge.name = OWASP_STAFF_BADGE_NAME
        mock_badge.id = 1
        mock_badge_get_or_create.return_value = (mock_badge, False)

        # Set up employee mocks
        mock_employee = MagicMock()
        mock_former_employee = MagicMock()
        mock_employee.id = 456
        mock_former_employee.id = 123
        mock_employees, _ = make_mock_employees(mock_employee)
        mock_former_employees = make_mock_former_employees(mock_former_employee)

        mock_user_filter.side_effect = user_filter_side_effect_factory(
            mock_employees, mock_former_employees
        )

        mock_user_badge_get_or_create.return_value = (MagicMock(), True)

        out = StringIO()
        call_command("nest_update_badges", stdout=out)

        # Assert correct badge assignment and removal calls
        mock_user_badge_get_or_create.assert_any_call(user=mock_employee, badge=mock_badge)
        mock_user_badge_filter.assert_any_call(
            user_id__in=mock_former_employees.values_list.return_value, badge=mock_badge
        )

        # Check command output
        output = out.getvalue()
        assert "User badges sync completed" in output
        assert any(s in output for s in ("Added badge to 1 staff", "Added badge to 1 employees"))
        assert any(
            s in output
            for s in ("Removed badge from 1 non-staff", "Removed badge from 1 non-employees")
        )

    @patch("apps.nest.management.commands.nest_update_badges.ContentType.objects.get_for_model")
    @patch("apps.nest.management.commands.nest_update_badges.EntityMember.objects.filter")
    @patch("apps.nest.management.commands.nest_update_badges.UserBadge.objects.get_or_create")
    @patch("apps.nest.management.commands.nest_update_badges.UserBadge.objects.filter")
    @patch("apps.nest.management.commands.nest_update_badges.Badge.objects.get_or_create")
    @patch("apps.nest.management.commands.nest_update_badges.User.objects.filter")
    def test_badge_creation(
        self, mock_user_filter, mock_badge_get_or_create, mock_user_badge_filter, mock_user_badge_get_or_create, mock_entity_member_filter, mock_content_type
    ):
        # Mock ContentType
        mock_project_content_type = MagicMock()
        mock_content_type.return_value = mock_project_content_type

        # Set up badge creation mocks
        mock_staff_badge = MagicMock()
        mock_staff_badge.name = OWASP_STAFF_BADGE_NAME
        mock_leader_badge = MagicMock()
        mock_leader_badge.name = PROJECT_LEADER_BADGE_NAME
        mock_badge_get_or_create.side_effect = [
            (mock_staff_badge, True),
            (mock_leader_badge, True),
        ]

        # Set up empty querysets
        mock_employees = MagicMock()
        mock_employees.__iter__.return_value = iter([])
        mock_employees.count.return_value = 0
        mock_employees.exclude.return_value = mock_employees
        mock_employees.values_list.return_value = []
        mock_employees.exclude.return_value.values_list.return_value = []
        mock_employees.exclude.return_value.distinct.return_value = mock_employees
        mock_employees.exclude.return_value.distinct.return_value.values_list.return_value = []

        mock_former_employees = MagicMock()
        mock_former_employees.__iter__.return_value = iter([])
        mock_former_employees.count.return_value = 0
        mock_former_employees.values_list.return_value = []
        mock_former_employees.distinct.return_value = mock_former_employees

        # Mock EntityMember for project leaders (empty)
        mock_entity_members = MagicMock()
        mock_entity_members.values_list.return_value.distinct.return_value = []
        mock_entity_member_filter.return_value = mock_entity_members

        mock_user_filter.side_effect = [
            mock_employees,  # Staff without badge
            mock_former_employees,  # Non-staff with badge
            mock_employees,  # Leaders without badge
            mock_former_employees,  # Non-leaders with badge
        ]

        out = StringIO()
        call_command("nest_update_badges", stdout=out)

        # Check both badges were created
        assert mock_badge_get_or_create.call_count == 2
        output = out.getvalue()
        assert f"Created badge: {mock_staff_badge.name}" in output
        assert f"Created badge: {mock_leader_badge.name}" in output

    @patch("apps.nest.management.commands.nest_update_badges.ContentType.objects.get_for_model")
    @patch("apps.nest.management.commands.nest_update_badges.EntityMember.objects.filter")
    @patch("apps.nest.management.commands.nest_update_badges.UserBadge.objects.get_or_create")
    @patch("apps.nest.management.commands.nest_update_badges.UserBadge.objects.filter")
    @patch("apps.nest.management.commands.nest_update_badges.Badge.objects.get_or_create")
    @patch("apps.nest.management.commands.nest_update_badges.User.objects.filter")
    def test_command_idempotency(
        self, mock_user_filter, mock_badge_get_or_create, mock_user_badge_filter, mock_user_badge_get_or_create, mock_entity_member_filter, mock_content_type
    ):
        """Test that running the command multiple times has the same effect as running it once."""
        # Mock ContentType
        mock_project_content_type = MagicMock()
        mock_content_type.return_value = mock_project_content_type

        # Set up badge mocks
        mock_staff_badge = MagicMock()
        mock_staff_badge.name = OWASP_STAFF_BADGE_NAME
        mock_staff_badge.id = 1
        mock_leader_badge = MagicMock()
        mock_leader_badge.name = PROJECT_LEADER_BADGE_NAME
        mock_leader_badge.id = 2
        mock_badge_get_or_create.side_effect = [
            (mock_staff_badge, False),
            (mock_leader_badge, False),
            (mock_staff_badge, False),
            (mock_leader_badge, False),
        ]

        # Set up employee mock that already has the badge
        mock_employee_with_badge = MagicMock()
        mock_employees = MagicMock()
        mock_employees.__iter__.return_value = iter([mock_employee_with_badge])
        
        # Configure the exclude().distinct() chain properly
        mock_excluded = MagicMock()
        mock_excluded.count.return_value = 0
        mock_excluded.values_list.return_value = []
        mock_excluded.distinct.return_value = mock_excluded
        mock_excluded.distinct.return_value.count.return_value = 0
        mock_employees.exclude.return_value = mock_excluded

        # No former employees have the badge
        mock_non_employees_filter = MagicMock()
        mock_non_employees_filter.count.return_value = 0
        mock_non_employees_filter.__iter__.return_value = iter([])
        mock_non_employees_filter.values_list.return_value = []
        mock_non_employees_filter.distinct.return_value = mock_non_employees_filter
        mock_non_employees_filter.exclude.return_value = mock_non_employees_filter
        mock_non_employees_filter.exclude.return_value.distinct.return_value = mock_non_employees_filter
        mock_non_employees_filter.exclude.return_value.distinct.return_value.count.return_value = 0

        # Mock EntityMember for project leaders (empty)
        mock_entity_members = MagicMock()
        mock_entity_members.values_list.return_value.distinct.return_value = []
        mock_entity_member_filter.return_value = mock_entity_members

        # Configure filter side effects for two command runs (4 calls per run)
        mock_user_filter.side_effect = [
            mock_employees,  # Run 1: Staff without badge
            mock_non_employees_filter,  # Run 1: Non-staff with badge
            mock_employees,  # Run 1: Leaders without badge
            mock_non_employees_filter,  # Run 1: Non-leaders with badge
            mock_employees,  # Run 2: Staff without badge
            mock_non_employees_filter,  # Run 2: Non-staff with badge
            mock_employees,  # Run 2: Leaders without badge
            mock_non_employees_filter,  # Run 2: Non-leaders with badge
        ]

        # First run
        out1 = StringIO()
        call_command("nest_update_badges", stdout=out1)

        # Second run
        out2 = StringIO()
        call_command("nest_update_badges", stdout=out2)

        # Check both outputs contain zero-count messages for staff and leaders
        assert any(
            s in out1.getvalue() for s in ("Added badge to 0 employees", "Added badge to 0 staff")
        )
        assert "Added badge to 0 project leaders" in out1.getvalue()
        assert any(
            s in out1.getvalue()
            for s in ("Removed badge from 0 non-employees", "Removed badge from 0 non-staff")
        )
        assert "Removed badge from 0 non-leaders" in out1.getvalue()
        assert any(
            s in out2.getvalue() for s in ("Added badge to 0 employees", "Added badge to 0 staff")
        )
        assert "Added badge to 0 project leaders" in out2.getvalue()
        assert any(
            s in out2.getvalue()
            for s in ("Removed badge from 0 non-employees", "Removed badge from 0 non-staff")
        )
        assert "Removed badge from 0 non-leaders" in out2.getvalue()

    @patch("apps.nest.management.commands.nest_update_badges.ContentType.objects.get_for_model")
    @patch("apps.nest.management.commands.nest_update_badges.EntityMember.objects.filter")
    @patch("apps.nest.management.commands.nest_update_badges.UserBadge.objects.get_or_create")
    @patch("apps.nest.management.commands.nest_update_badges.UserBadge.objects.filter")
    @patch("apps.nest.management.commands.nest_update_badges.Badge.objects.get_or_create")
    @patch("apps.nest.management.commands.nest_update_badges.User.objects.filter")
    def test_sync_project_leader_badge(
        self,
        mock_user_filter,
        mock_badge_get_or_create,
        mock_user_badge_filter,
        mock_user_badge_get_or_create,
        mock_entity_member_filter,
        mock_content_type,
    ):
        # Mock ContentType
        mock_project_content_type = MagicMock()
        mock_content_type.return_value = mock_project_content_type

        # Set up badge mocks for both staff and project leader badges
        mock_staff_badge = MagicMock()
        mock_staff_badge.name = OWASP_STAFF_BADGE_NAME
        mock_staff_badge.id = 1

        mock_leader_badge = MagicMock()
        mock_leader_badge.name = PROJECT_LEADER_BADGE_NAME
        mock_leader_badge.id = 2

        mock_badge_get_or_create.side_effect = [
            (mock_staff_badge, False),
            (mock_leader_badge, False),
        ]

        # Set up project leader mocks
        mock_leader = MagicMock()
        mock_leader.id = 789
        mock_former_leader = MagicMock()
        mock_former_leader.id = 456

        # Mock EntityMember queryset for project leaders
        mock_entity_members = MagicMock()
        mock_entity_members.values_list.return_value.distinct.return_value = [mock_leader.id]
        mock_entity_member_filter.return_value = mock_entity_members

        # Mock User querysets
        mock_leaders_without_badge = MagicMock()
        mock_leaders_without_badge.__iter__.return_value = iter([mock_leader])
        mock_leaders_without_badge.count.return_value = 1
        mock_leaders_without_badge.exclude.return_value = mock_leaders_without_badge

        mock_non_leaders = MagicMock()
        mock_non_leaders.__iter__.return_value = iter([mock_former_leader])
        mock_non_leaders.count.return_value = 1
        mock_non_leaders.values_list.return_value = [mock_former_leader.id]
        mock_non_leaders.distinct.return_value = mock_non_leaders
        mock_non_leaders.exclude.return_value = mock_leaders_without_badge

        # Set up empty mocks for staff badge (to avoid interference)
        mock_empty = MagicMock()
        mock_empty.__iter__.return_value = iter([])
        mock_empty.count.return_value = 0
        mock_empty.values_list.return_value = []
        mock_empty.distinct.return_value = mock_empty
        mock_empty.exclude.return_value = mock_empty

        mock_user_filter.side_effect = [
            mock_empty,  # Staff without badge
            mock_empty,  # Non-staff with badge
            mock_leaders_without_badge,  # Project leaders without badge
            mock_non_leaders,  # Non-leaders with badge
        ]

        mock_user_badge_get_or_create.return_value = (MagicMock(), True)

        out = StringIO()
        call_command("nest_update_badges", stdout=out)

        # Assert correct badge assignment for project leaders
        mock_user_badge_get_or_create.assert_any_call(user=mock_leader, badge=mock_leader_badge)
        # The actual call uses the mock's values_list().distinct() chain
        assert mock_user_badge_filter.call_count >= 1

        # Check command output
        output = out.getvalue()
        assert "User badges sync completed" in output
        assert "Added badge to 1 project leaders" in output
        assert "non-leaders" in output
