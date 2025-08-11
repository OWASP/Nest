"""Tests for the sync_user_badges management command."""

from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command

OWASP_EMPLOYEE_BADGE_NAME = "OWASP Employee"


class TestSyncUserBadgesCommand:
    """Test the sync_user_badges management command."""

    @patch("apps.owasp.models.badge.Badge.objects.get_or_create")
    @patch("apps.github.models.user.User.objects.filter")
    def test_sync_owasp_employee_badge(self, mock_user_filter, mock_badge_get_or_create):
        # Set up badge mock
        mock_badge = MagicMock()
        mock_badge.name = OWASP_EMPLOYEE_BADGE_NAME
        mock_badge.id = 1
        mock_badge_get_or_create.return_value = (mock_badge, False)

        # Set up employee mocks - with exclude() method properly mocked
        mock_employee = MagicMock()
        mock_employees = MagicMock()
        mock_employees_without_badge = MagicMock()
        mock_employees_without_badge.__iter__.return_value = [mock_employee]
        mock_employees_without_badge.count.return_value = 1
        mock_employees.exclude.return_value = mock_employees_without_badge

        # Set up former employee mocks
        mock_former_employee = MagicMock()
        mock_former_employees = MagicMock()
        mock_former_employees.__iter__.return_value = [mock_former_employee]
        mock_former_employees.count.return_value = 1

        mock_user_filter.side_effect = [
            mock_employees,
            mock_former_employees,
        ]

        # Call the command
        out = StringIO()
        call_command("github_sync_user_badges", stdout=out)

        # Verify badge assignments
        mock_employee.badges.add.assert_called_once_with(mock_badge)
        mock_former_employee.badges.remove.assert_called_once_with(mock_badge)

        # Check command output
        output = out.getvalue()
        assert "User badges sync completed" in output
        assert "Added badge to 1 employees" in output
        assert "Removed badge from 1 non-employees" in output

    @patch("apps.owasp.models.badge.Badge.objects.get_or_create")
    @patch("apps.github.models.user.User.objects.filter")
    def test_badge_creation(self, mock_user_filter, mock_badge_get_or_create):
        # Set up badge creation mock
        mock_badge = MagicMock()
        mock_badge.name = OWASP_EMPLOYEE_BADGE_NAME
        mock_badge_get_or_create.return_value = (mock_badge, True)

        # Set up empty querysets
        mock_employees = MagicMock()
        mock_employees.__iter__.return_value = []
        mock_employees.count.return_value = 0
        mock_former_employees = MagicMock()
        mock_former_employees.__iter__.return_value = []
        mock_former_employees.count.return_value = 0

        mock_user_filter.side_effect = [mock_employees, mock_former_employees]

        # Call the command
        out = StringIO()
        call_command("github_sync_user_badges", stdout=out)

        # Verify badge creation and defaults

        mock_badge_get_or_create.assert_called_once_with(
            name="OWASP Employee",
            defaults={
                "description": "Official OWASP Employee",
                "css_class": "fa-user-shield",
                "weight": 100,
            },
        )

        # Check command output
        output = out.getvalue()
        assert f"Created badge: {mock_badge.name}" in output

    @patch("apps.owasp.models.badge.Badge.objects.get_or_create")
    @patch("apps.github.models.user.User.objects.filter")
    def test_command_idempotency(self, mock_user_filter, mock_badge_get_or_create):
        """Test that running the command multiple times has the same effect as running it once."""
        # Set up badge mock
        mock_badge = MagicMock()
        mock_badge.name = OWASP_EMPLOYEE_BADGE_NAME
        mock_badge.id = 1
        mock_badge_get_or_create.return_value = (mock_badge, False)

        # Set up employee mock that already has the badge
        mock_employee_with_badge = MagicMock()
        # This employee already has the badge
        mock_employee_with_badge.badges.filter.return_value.exists.return_value = True
        mock_employees = MagicMock()
        mock_employees.__iter__.return_value = [mock_employee_with_badge]
        # Using exclude() would return 0 employees without the badge
        mock_employees.exclude.return_value = MagicMock()
        mock_employees.exclude.return_value.count.return_value = 0

        # No former employees have the badge
        mock_non_employees_filter = MagicMock()
        mock_non_employees_filter.count.return_value = 0
        mock_non_employees_filter.__iter__.return_value = []

        # Configure filter side effects for two command runs
        mock_user_filter.side_effect = [
            mock_employees,
            mock_non_employees_filter,
            mock_employees,
            mock_non_employees_filter,
        ]

        # First run
        out1 = StringIO()
        call_command("github_sync_user_badges", stdout=out1)

        # Second run
        out2 = StringIO()
        call_command("github_sync_user_badges", stdout=out2)

        # Verify no add/remove operations were performed
        mock_employee_with_badge.badges.add.assert_not_called()

        # Check both outputs contain zero-count messages
        assert "Added badge to 0 employees" in out1.getvalue()
        assert "Removed badge from 0 non-employees" in out1.getvalue()
        assert "Added badge to 0 employees" in out2.getvalue()
        assert "Removed badge from 0 non-employees" in out2.getvalue()
