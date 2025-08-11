"""Tests for the sync_user_badges management command."""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command


@pytest.fixture
def mock_badge():
    badge = MagicMock()
    badge.name = "OWASP Employee"
    badge.css_class = "fa-user-shield"
    badge.id = 1
    return badge


class TestSyncUserBadgesCommand:
    """Test the sync_user_badges management command."""

    @patch("apps.owasp.models.badge.Badge.objects.get_or_create")
    @patch("apps.github.models.user.User.objects.filter")
    def test_sync_owasp_employee_badge(self, mock_user_filter, mock_badge_get_or_create):
        # Set up badge mock
        mock_badge = MagicMock()
        mock_badge.name = "OWASP Employee"
        mock_badge.id = 1
        mock_badge_get_or_create.return_value = (mock_badge, False)

        # Set up employee mocks
        mock_employee = MagicMock()
        mock_employee.badges.filter.return_value.exists.return_value = False
        mock_employees = MagicMock()
        mock_employees.__iter__.return_value = [mock_employee]
        mock_employees.count.return_value = 1

        # Set up former employee mocks
        mock_former_employee = MagicMock()
        mock_former_employees = MagicMock()
        mock_former_employees.__iter__.return_value = [mock_former_employee]
        mock_former_employees.count.return_value = 1

        # Set up the double filter behavior
        mock_non_employees_first_filter = MagicMock()
        mock_non_employees_first_filter.filter.return_value = mock_former_employees

        # Configure filter side effects
        mock_user_filter.side_effect = [
            mock_employees,  # is_owasp_employee=True
            # is_owasp_employee=False, will need .filter(badges=badge)
            mock_non_employees_first_filter,
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
        mock_badge.name = "OWASP Employee"
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

        # Verify badge creation
        mock_badge_get_or_create.assert_called_once()

        # Check command output
        output = out.getvalue()
        assert f"Created badge: {mock_badge.name}" in output
