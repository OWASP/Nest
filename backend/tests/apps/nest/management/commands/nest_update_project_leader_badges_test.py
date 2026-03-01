"""Tests for project leader badge command."""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.test import SimpleTestCase

from apps.nest.management.commands.nest_update_project_leader_badges import Command


class TestProjectLeaderBadgeCommand(SimpleTestCase):
    def test_has_correct_metadata(self):
        assert Command.badge_name == "OWASP Project Leader"
        assert Command.badge_weight == 90
        assert Command.badge_css_class == "star"

    @patch("apps.nest.management.commands.nest_update_project_leader_badges.User")
    @patch("apps.nest.management.commands.nest_update_project_leader_badges.EntityMember")
    @patch("apps.nest.management.commands.nest_update_project_leader_badges.Project")
    @patch("apps.nest.management.commands.nest_update_project_leader_badges.ContentType")
    @patch("apps.nest.management.commands.base_badge_command.UserBadge")
    @patch("apps.nest.management.commands.base_badge_command.Badge")
    def test_command_runs(
        self, mock_badge, mock_user_badge, mock_ct, mock_project, mock_em, mock_user
    ):
        badge = MagicMock()
        badge.name = "OWASP Project Leader"
        mock_badge.objects.get_or_create.return_value = (badge, False)

        mock_ct.objects.get_for_model.return_value = MagicMock()
        leaders_qs = MagicMock()
        mock_em.objects.filter.return_value = leaders_qs
        leaders_qs.values_list.return_value = []

        qs = MagicMock()
        qs.exclude.return_value = []
        qs.distinct.return_value = qs
        mock_user.objects.filter.return_value = qs
        mock_user_badge.objects.filter.return_value.exclude.return_value.count.return_value = 0

        out = StringIO()
        call_command("nest_update_project_leader_badges", stdout=out)
        assert "Project Leader" in out.getvalue()

    @patch("apps.nest.management.commands.nest_update_project_leader_badges.ContentType")
    @patch("apps.nest.management.commands.base_badge_command.Badge")
    @patch(
        "apps.nest.management.commands.nest_update_project_leader_badges.EntityMember.objects.filter",
        side_effect=Exception("error"),
    )
    def test_handles_errors(self, mock_filter, mock_badge, mock_content_type):
        badge = MagicMock()
        badge.name = "OWASP Project Leader"
        mock_badge.objects.get_or_create.return_value = (badge, False)
        mock_content_type.objects.get_for_model.return_value = MagicMock()

        with pytest.raises(Exception, match="error"):
            call_command("nest_update_project_leader_badges", stdout=StringIO())
