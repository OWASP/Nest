"""Tests for staff badge command."""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.test import SimpleTestCase

from apps.nest.management.commands.nest_update_staff_badge import Command


class TestStaffBadgeCommand(SimpleTestCase):
    def test_has_correct_metadata(self):
        assert Command.badge_name == "OWASP Staff"
        assert Command.badge_weight == 100

    @patch("apps.nest.management.commands.nest_update_staff_badge.User")
    @patch("apps.nest.management.commands.base_badge_command.UserBadge")
    @patch("apps.nest.management.commands.base_badge_command.Badge")
    def test_command_runs(self, mock_badge, mock_user_badge, mock_user):
        badge = MagicMock()
        badge.name = "OWASP Staff"
        mock_badge.objects.get_or_create.return_value = (badge, False)

        qs = MagicMock()
        qs.exclude.return_value = []
        mock_user.objects.filter.return_value = qs
        mock_user_badge.objects.filter.return_value.exclude.return_value.count.return_value = 0

        out = StringIO()
        call_command("nest_update_staff_badge", stdout=out)
        assert "OWASP Staff" in out.getvalue()

    @patch("apps.nest.management.commands.base_badge_command.Badge")
    @patch(
        "apps.nest.management.commands.nest_update_staff_badge.User.objects.filter",
        side_effect=Exception("error"),
    )
    def test_handles_errors(self, mock_filter, mock_badge):
        badge = MagicMock()
        badge.name = "OWASP Staff"
        mock_badge.objects.get_or_create.return_value = (badge, False)

        with pytest.raises(Exception, match="error"):
            call_command("nest_update_staff_badge", stdout=StringIO())
