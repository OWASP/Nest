"""Tests for the nest_update_badges management command."""

from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command

from apps.nest.management.commands.nest_update_badges import OWASP_STAFF_BADGE_NAME


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
    key_to_check = "owasp_profile__is_owasp_staff"
    legacy_key_to_check = "is_owasp_staff"
    if hasattr(arg, "children"):
        for key, value in arg.children:
            if key in (key_to_check, legacy_key_to_check):
                return value
    if isinstance(arg, dict):
        if key_to_check in arg:
            return arg[key_to_check]
        if legacy_key_to_check in arg:
            return arg[legacy_key_to_check]
    if isinstance(arg, tuple) and len(arg) == 2 and arg[0] in (key_to_check, legacy_key_to_check):
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
        staff_value = kwargs.get("owasp_profile__is_owasp_staff", kwargs.get("is_owasp_staff"))
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

    @patch("apps.nest.management.commands.nest_update_badges.UserBadge.objects.filter")
    @patch("apps.nest.management.commands.nest_update_badges.Badge.objects.get_or_create")
    @patch("apps.nest.management.commands.nest_update_badges.User.objects.filter")
    def test_badge_creation(
        self, mock_user_filter, mock_badge_get_or_create, mock_user_badge_filter
    ):
        # Set up badge creation mock
        mock_badge = MagicMock()
        mock_badge.name = OWASP_STAFF_BADGE_NAME
        mock_badge_get_or_create.return_value = (mock_badge, True)

        # Set up a detailed mock for an empty queryset
        mock_empty_queryset = MagicMock()
        mock_empty_queryset.count.return_value = 0
        mock_empty_queryset.exclude.return_value = mock_empty_queryset
        mock_empty_queryset.distinct.return_value = mock_empty_queryset
        mock_empty_queryset.values_list.return_value = []

        # The command makes up to 4 calls to User.objects.filter for employees
        # and non-employees, so we provide a mock for each.
        mock_user_filter.side_effect = [
            mock_empty_queryset,
            mock_empty_queryset,
            mock_empty_queryset,
            mock_empty_queryset,
        ]

        out = StringIO()
        call_command("nest_update_badges", stdout=out)

        mock_badge_get_or_create.assert_called_once_with(
            name=OWASP_STAFF_BADGE_NAME,
            defaults={
                "description": "Official OWASP Staff",
                "css_class": "fa-user-shield",
                "weight": 100,
            },
        )
        output = out.getvalue()
        assert f"Created badge: {mock_badge.name}" in output
        # Verify that no badges were removed since the querysets are empty
        mock_user_badge_filter.assert_not_called()

    @patch("apps.nest.management.commands.nest_update_badges.UserBadge.objects.filter")
    @patch("apps.nest.management.commands.nest_update_badges.Badge.objects.get_or_create")
    @patch("apps.nest.management.commands.nest_update_badges.User.objects.filter")
    def test_command_idempotency(
        self, mock_user_filter, mock_badge_get_or_create, mock_user_badge_filter
    ):
        """Test that running the command multiple times has the same effect as running it once."""
        # Set up badge mock
        mock_badge = MagicMock()
        mock_badge.name = OWASP_STAFF_BADGE_NAME
        mock_badge.id = 1
        mock_badge_get_or_create.return_value = (mock_badge, False)


        mock_employees_with_badge = MagicMock()
        mock_employees_with_badge.exclude.return_value.count.return_value = 0


        mock_non_employees = MagicMock()
        mock_non_employees.distinct.return_value.count.return_value = 0

        mock_user_filter.side_effect = user_filter_side_effect_factory(
            mock_employees_with_badge, mock_non_employees
        )

        # First run
        out1 = StringIO()
        call_command("nest_update_badges", stdout=out1)

        # Second run
        out2 = StringIO()
        call_command("nest_update_badges", stdout=out2)

        # Check both outputs contain zero-count messages
        assert "Added badge to 0 employees" in out1.getvalue()
        assert "Removed badge from 0 non-employees" in out1.getvalue()
        assert "Added badge to 0 employees" in out2.getvalue()
        assert "Removed badge from 0 non-employees" in out2.getvalue()

        mock_user_badge_filter.return_value.update.assert_not_called()
