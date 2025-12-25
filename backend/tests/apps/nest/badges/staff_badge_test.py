"""Tests for the OWASP Staff badge handler."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.nest.badges.staff_badge import OWASPStaffBadgeHandler


class TestOWASPStaffBadgeHandler(SimpleTestCase):
    
    @patch("apps.nest.badges.staff_badge.User")
    def test_get_eligible_users_filters_staff(self, mock_user_model):
        """Test that get_eligible_users filters for is_owasp_staff=True."""
        handler = OWASPStaffBadgeHandler()
        handler.get_eligible_users()

        mock_user_model.objects.filter.assert_called_once_with(is_owasp_staff=True)