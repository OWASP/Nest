"""Test cases for Nest Calendar Events permissions."""

from unittest.mock import MagicMock, patch

from apps.nest.auth.calendar_events import has_calendar_events_permission
from apps.owasp.models.entity_member import EntityMember
from apps.slack.models.member import Member


class TestCalendarEventsPermissions:
    """Test cases for Nest Calendar Events permissions."""

    @patch("apps.nest.auth.calendar_events.Member.objects.get")
    @patch("apps.nest.auth.calendar_events.EntityMember.objects.filter")
    def test_user_with_leader_role(self, mock_filter, mock_get):
        """Test user with leader role has permission."""
        mock_member = MagicMock()
        mock_member.user = MagicMock()
        mock_get.return_value = mock_member
        mock_filter.return_value.exists.return_value = True

        assert has_calendar_events_permission("U123456") is True
        mock_get.assert_called_once_with(slack_user_id="U123456")
        mock_filter.assert_called_once_with(member=mock_member.user, role=EntityMember.Role.LEADER)

    @patch("apps.nest.auth.calendar_events.Member.objects.get")
    @patch("apps.nest.auth.calendar_events.EntityMember.objects.filter")
    def test_user_with_no_leader_role(self, mock_filter, mock_get):
        """Test user with no leader role has no permission."""
        mock_member = MagicMock()
        mock_member.user = MagicMock()
        mock_get.return_value = mock_member
        mock_filter.return_value.exists.return_value = False

        assert has_calendar_events_permission("U123456") is False
        mock_get.assert_called_once_with(slack_user_id="U123456")
        mock_filter.assert_called_once_with(member=mock_member.user, role=EntityMember.Role.LEADER)

    @patch("apps.nest.auth.calendar_events.Member.objects.get")
    def test_user_not_found(self, mock_get):
        """Test user not found has no permission."""
        mock_get.side_effect = Member.DoesNotExist

        assert has_calendar_events_permission("U123456") is False
        mock_get.assert_called_once_with(slack_user_id="U123456")
