"""Tests for the BaseBadgeHandler class."""

from io import StringIO
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.nest.badges.base import BaseBadgeHandler


class ConcreteTestHandler(BaseBadgeHandler):
    """Concrete implementation of BaseBadgeHandler for testing purposes."""

    name = "Test Badge"
    description = "Test Description"
    css_class = "fa-test"
    weight = 50

    def get_eligible_users(self):
        return MagicMock()


class TestBaseBadgeHandler(SimpleTestCase):
    """Tests for the BaseBadgeHandler logic."""

    def setUp(self):
        self.out = StringIO()
        self.handler = ConcreteTestHandler(stdout=self.out)

    @patch("apps.nest.badges.base.UserBadge")
    @patch("apps.nest.badges.base.Badge")
    def test_process_creates_badge(self, mock_badge_model, mock_user_badge_model):
        """Test that the badge definition is created or updated."""
        mock_badge_instance = MagicMock()
        mock_badge_instance.name = "Test Badge"
        mock_badge_model.objects.get_or_create.return_value = (mock_badge_instance, True)

        mock_qs = MagicMock()
        mock_qs.exclude.return_value = []
        self.handler.get_eligible_users = MagicMock(return_value=mock_qs)

        self.handler.process()

        mock_badge_model.objects.get_or_create.assert_called_with(
            name="Test Badge",
            defaults={
                "description": "Test Description",
                "css_class": "fa-test",
                "weight": 50,
            },
        )
        assert "Created badge: 'Test Badge'" in self.out.getvalue()

    @patch("apps.nest.badges.base.UserBadge")
    @patch("apps.nest.badges.base.Badge")
    def test_process_adds_badge_to_eligible_users(self, mock_badge_model, mock_user_badge_model):
        """Test that eligible users receive the badge."""
        mock_badge = MagicMock()
        mock_badge_model.objects.get_or_create.return_value = (mock_badge, False)

        user_1 = MagicMock(id=1)
        mock_eligible_qs = MagicMock()

        mock_eligible_qs.exclude.return_value = [user_1]
        self.handler.get_eligible_users = MagicMock(return_value=mock_eligible_qs)

        mock_user_badge = MagicMock()
        mock_user_badge.is_active = False
        mock_user_badge_model.objects.get_or_create.return_value = (mock_user_badge, False)
        self.handler.process()

        mock_user_badge_model.objects.get_or_create.assert_called_with(
            user=user_1, badge=mock_badge
        )
        assert mock_user_badge.is_active is True
        mock_user_badge.save.assert_called_with(update_fields=["is_active"])
        assert "Added 'Test Badge' badge to 1 users" in self.out.getvalue()

    @patch("apps.nest.badges.base.UserBadge")
    @patch("apps.nest.badges.base.Badge")
    def test_process_revokes_badge_from_ineligible_users(
        self, mock_badge_model, mock_user_badge_model
    ):
        """Test that ineligible users lose the badge."""
        mock_badge = MagicMock()
        mock_badge_model.objects.get_or_create.return_value = (mock_badge, False)

        mock_eligible_qs = MagicMock()
        mock_eligible_qs.exclude.return_value = []
        self.handler.get_eligible_users = MagicMock(return_value=mock_eligible_qs)

        mock_revocation_qs = MagicMock()
        mock_revocation_qs.count.return_value = 5
        mock_active_badges = MagicMock()

        mock_user_badge_model.objects.filter.return_value = mock_active_badges
        mock_active_badges.exclude.return_value = mock_revocation_qs
        self.handler.process()

        mock_revocation_qs.update.assert_called_with(is_active=False)
        assert "Removed 'Test Badge' badge from 5 users" in self.out.getvalue()
