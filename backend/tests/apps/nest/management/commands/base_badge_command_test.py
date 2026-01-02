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
