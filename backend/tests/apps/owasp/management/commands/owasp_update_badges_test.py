"""Tests for the owasp_update_badges management command."""

from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command

from apps.owasp.management.commands.owasp_update_badges import OWASP_STAFF_BADGE_NAME


class TestSyncUserBadgesCommand:
    """Test the sync_user_badges management command."""

    @patch("apps.owasp.models.badge.Badge.objects.get_or_create")
    @patch("apps.github.models.user.User.objects.filter")
    def test_sync_owasp_staff_badge(self, mock_user_filter, mock_badge_get_or_create):
        # Set up badge mock
        mock_badge = MagicMock()
        mock_badge.name = OWASP_STAFF_BADGE_NAME
        mock_badge.id = 1
        mock_badge_get_or_create.return_value = (mock_badge, False)

        # Set up employee mocks - with exclude() method properly mocked
        mock_employee = MagicMock()
        mock_employees = MagicMock()
        mock_employees_without_badge = MagicMock()
        mock_employees_without_badge.__iter__.return_value = iter([mock_employee])
        mock_employees_without_badge.count.return_value = 1
        mock_employees.exclude.return_value = mock_employees_without_badge

        # Set up former employee mocks
        mock_former_employee = MagicMock()
        mock_former_employees = MagicMock()
        mock_former_employees.__iter__.return_value = iter([mock_former_employee])
        mock_former_employees.count.return_value = 1

        def user_filter_side_effect(*args, **kwargs):
            # Handle keyword arguments
            if kwargs.get("is_owasp_staff") is True:
                return mock_employees
            if kwargs.get("is_owasp_staff") is False:
                return mock_former_employees

            # Handle positional arguments
            result = None
            for arg in args:
                result = check_arg_for_staff_status(arg)
                if result:
                    return result

            return MagicMock()

        def check_arg_for_staff_status(arg):
            """Extract the staff status value and return the appropriate mock."""
            # Extract the staff status value based on argument type
            is_staff_value = None

            # Q objects
            if hasattr(arg, "children"):
                for key, value in arg.children:
                    if key == "is_owasp_staff":
                        is_staff_value = value
                        break

            # Dict case
            elif isinstance(arg, dict) and "is_owasp_staff" in arg:
                is_staff_value = arg["is_owasp_staff"]

            # Tuple case
            elif isinstance(arg, tuple) and len(arg) == 2 and arg[0] == "is_owasp_staff":
                is_staff_value = arg[1]

            # Return the appropriate mock based on the extracted value
            if is_staff_value is True:
                return mock_employees
            if is_staff_value is False:
                return mock_former_employees

            return None

        mock_user_filter.side_effect = user_filter_side_effect

        out = StringIO()
        call_command("owasp_update_badges", stdout=out)

        # Collect all positional args from add/remove calls
        add_args = []
        for call in mock_badge.users.add.call_args_list:
            add_args.extend(call.args)
        remove_args = []
        for call in mock_badge.users.remove.call_args_list:
            remove_args.extend(call.args)

        # Assert expected employees are present/absent in the calls
        assert mock_employee in add_args
        assert mock_former_employee not in add_args
        assert mock_former_employee in remove_args
        assert mock_employee not in remove_args

        # Check command output
        output = out.getvalue()
        assert "User badges sync completed" in output
        assert any(s in output for s in ("Added badge to 1 staff", "Added badge to 1 employees"))
        assert any(
            s in output
            for s in ("Removed badge from 1 non-staff", "Removed badge from 1 non-employees")
        )

    @patch("apps.owasp.models.badge.Badge.objects.get_or_create")
    @patch("apps.github.models.user.User.objects.filter")
    def test_badge_creation(self, mock_user_filter, mock_badge_get_or_create):
        # Set up badge creation mock
        mock_badge = MagicMock()
        mock_badge.name = OWASP_STAFF_BADGE_NAME
        mock_badge_get_or_create.return_value = (mock_badge, True)

        # Set up empty querysets
        mock_employees = MagicMock()
        mock_employees.__iter__.return_value = iter([])
        mock_employees.count.return_value = 0
        mock_employees.exclude.return_value = (
            mock_employees  # Ensure exclude() yields an empty iterable
        )

        mock_former_employees = MagicMock()
        mock_former_employees.__iter__.return_value = iter([])
        mock_former_employees.count.return_value = 0
        mock_former_employees.exclude.return_value = mock_former_employees

        mock_user_filter.side_effect = [mock_employees, mock_former_employees]

        out = StringIO()
        call_command("owasp_update_badges", stdout=out)

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

    @patch("apps.owasp.models.badge.Badge.objects.get_or_create")
    @patch("apps.github.models.user.User.objects.filter")
    def test_command_idempotency(self, mock_user_filter, mock_badge_get_or_create):
        """Test that running the command multiple times has the same effect as running it once."""
        # Set up badge mock
        mock_badge = MagicMock()
        mock_badge.name = OWASP_STAFF_BADGE_NAME
        mock_badge.id = 1
        mock_badge_get_or_create.return_value = (mock_badge, False)

        # Set up employee mock that already has the badge
        mock_employee_with_badge = MagicMock()
        # This employee already has the badge
        mock_employee_with_badge.badges.filter.return_value.exists.return_value = True
        mock_employees = MagicMock()
        mock_employees.__iter__.return_value = iter([mock_employee_with_badge])
        # Using exclude() would return 0 employees without the badge
        mock_employees.exclude.return_value = MagicMock()
        mock_employees.exclude.return_value.count.return_value = 0

        # No former employees have the badge
        mock_non_employees_filter = MagicMock()
        mock_non_employees_filter.count.return_value = 0
        mock_non_employees_filter.__iter__.return_value = iter([])

        # Configure filter side effects for two command runs
        mock_user_filter.side_effect = [
            mock_employees,
            mock_non_employees_filter,
            mock_employees,
            mock_non_employees_filter,
        ]

        # First run
        out1 = StringIO()
        call_command("owasp_update_badges", stdout=out1)

        # Second run
        out2 = StringIO()
        call_command("owasp_update_badges", stdout=out2)

        # Verify no add/remove operations were performed
        mock_badge.users.add.assert_not_called()
        mock_badge.users.remove.assert_not_called()

        # Check both outputs contain zero-count messages (accept "employees" or "staff" wording)
        assert any(
            s in out1.getvalue() for s in ("Added badge to 0 employees", "Added badge to 0 staff")
        )
        assert any(
            s in out1.getvalue()
            for s in ("Removed badge from 0 non-employees", "Removed badge from 0 non-staff")
        )
        assert any(
            s in out2.getvalue() for s in ("Added badge to 0 employees", "Added badge to 0 staff")
        )
        assert any(
            s in out2.getvalue()
            for s in ("Removed badge from 0 non-employees", "Removed badge from 0 non-staff")
        )
