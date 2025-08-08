"""Tests for update_user_badges management command."""

from django.core.management import call_command
from django.test import TestCase

from apps.github.models.user import User
from apps.nest.models.badge import BadgeType, UserBadge
from apps.owasp.models.award import Award


class UpdateUserBadgesCommandTest(TestCase):
    """Test cases for update_user_badges command."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create(
            login="testuser",
            name="Test User",
            email="test@example.com",
            created_at="2020-01-01T00:00:00Z",
            updated_at="2020-01-01T00:00:00Z",
        )

        # Create a WASPY award for the user
        self.award = Award.objects.create(
            name="Test Person of the Year",
            category="WASPY",
            year=2024,
            award_type="award",
            winner_name="Test User",
            user=self.user,
        )

    def test_creates_waspy_badge_for_award_winner(self):
        """Test that WASPY badge is created for award winners."""
        # Run the command
        call_command("update_user_badges", verbosity=0)

        # Check that badge type was created
        badge_type = BadgeType.objects.get(name="WASPY Award Winner")
        assert badge_type.name == "WASPY Award Winner"

        # Check that user badge was created
        user_badge = UserBadge.objects.get(user=self.user, badge_type=badge_type)
        assert user_badge.user == self.user
        assert "Test Person of the Year" in user_badge.reason

    def test_removes_badge_when_award_removed(self):
        """Test that badge is removed when award is no longer associated."""
        # First run to create the badge
        call_command("update_user_badges", verbosity=0)

        badge_type = BadgeType.objects.get(name="WASPY Award Winner")
        assert UserBadge.objects.filter(user=self.user, badge_type=badge_type).exists()

        # Remove the award association
        self.award.user = None
        self.award.save()

        # Run command again
        call_command("update_user_badges", verbosity=0)

        # Check that badge was removed
        assert not UserBadge.objects.filter(user=self.user, badge_type=badge_type).exists()

    def test_dry_run_mode(self):
        """Test that dry run mode doesn't make changes."""
        # Run in dry run mode
        call_command("update_user_badges", dry_run=True, verbosity=0)

        # Check that no badge type or user badge was created
        assert not BadgeType.objects.filter(name="WASPY Award Winner").exists()
        assert not UserBadge.objects.filter(user=self.user).exists()

    def test_single_user_processing(self):
        """Test processing a single user by login."""
        # Run command for specific user
        call_command("update_user_badges", user_login="testuser", verbosity=0)

        # Check that badge was created
        badge_type = BadgeType.objects.get(name="WASPY Award Winner")
        user_badge = UserBadge.objects.get(user=self.user, badge_type=badge_type)
        assert user_badge.user == self.user
