"""Tests for base badge command."""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.test import SimpleTestCase

from apps.nest.management.commands.base_badge_command import BaseBadgeCommand


class MockCommand(BaseBadgeCommand):
    badge_css_class = "fa-test"
    badge_description = "Test"
    badge_name = "Test Badge"
    badge_weight = 50

    def get_eligible_users(self):
        return MagicMock()


class TestBaseBadgeCommand(SimpleTestCase):
    def test_requires_badge_name(self):
        class NoName(BaseBadgeCommand):
            def get_eligible_users(self):
                return MagicMock()

        with pytest.raises(ValueError, match="Badge name"):
            NoName().handle()

    @patch("apps.nest.management.commands.base_badge_command.UserBadge")
    @patch("apps.nest.management.commands.base_badge_command.Badge")
    def test_syncs_badge(self, mock_badge, mock_user_badge):
        badge = MagicMock()
        badge.name = "Test Badge"
        mock_badge.objects.get_or_create.return_value = (badge, False)

        qs = MagicMock()
        qs.exclude.return_value = []
        MockCommand.get_eligible_users = MagicMock(return_value=qs)

        mock_user_badge.objects.filter.return_value.exclude.return_value.count.return_value = 0

        out = StringIO()
        cmd = MockCommand()
        cmd.stdout = out
        cmd.handle()

        output = out.getvalue()
        assert "Test Badge" in output
        assert "synced successfully" in output

    @patch("apps.nest.management.commands.base_badge_command.UserBadge")
    @patch("apps.nest.management.commands.base_badge_command.Badge")
    def test_creates_new_badge(self, mock_badge, mock_user_badge):
        """Test that a new badge is created and logged."""
        badge = MagicMock()
        badge.name = "New Badge"
        # created=True indicates a new badge was created
        mock_badge.objects.get_or_create.return_value = (badge, True)

        qs = MagicMock()
        qs.exclude.return_value = []
        MockCommand.get_eligible_users = MagicMock(return_value=qs)

        mock_user_badge.objects.filter.return_value.exclude.return_value.count.return_value = 0

        out = StringIO()
        cmd = MockCommand()
        cmd.stdout = out
        cmd.badge_name = "New Badge"
        cmd.handle()

        output = out.getvalue()
        assert "Created badge: 'New Badge'" in output

    @patch("apps.nest.management.commands.base_badge_command.UserBadge")
    @patch("apps.nest.management.commands.base_badge_command.Badge")
    def test_removes_badges_from_users(self, mock_badge, mock_user_badge):
        """Test that badges are removed from users no longer eligible."""
        badge = MagicMock()
        badge.name = "Test Badge"
        mock_badge.objects.get_or_create.return_value = (badge, False)

        eligible_users = MagicMock()
        eligible_users.exclude.return_value = []
        MockCommand.get_eligible_users = MagicMock(return_value=eligible_users)

        # Simulate 3 users having their badges removed
        users_to_remove = MagicMock()
        users_to_remove.count.return_value = 3
        users_to_remove.update.return_value = 3
        mock_user_badge.objects.filter.return_value.exclude.return_value = users_to_remove

        out = StringIO()
        cmd = MockCommand()
        cmd.stdout = out
        cmd.handle()

        output = out.getvalue()
        assert "Removed 'Test Badge' badge from 3 users" in output
        users_to_remove.update.assert_called_once_with(is_active=False)
