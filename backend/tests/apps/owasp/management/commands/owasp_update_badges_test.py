"""Tests for owasp_update_badges management command."""

from django.core.management import call_command
from django.test import TestCase

from apps.github.models.user import User
from apps.nest.models.badge import Badge
from apps.owasp.models.award import Award

WASPY_BADGE_NAME = "WASPY Award Winner"


class TestOwaspUpdateBadges(TestCase):
    """Test cases for owasp_update_badges command."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create(login="winner1", name="Winner One")
        self.user2 = User.objects.create(login="not_winner", name="Not Winner")

        # Reviewed WASPY award -> should receive badge
        Award.objects.create(
            category=Award.Category.WASPY,
            name="Event Person of the Year - Winner One (2024)",
            description="",
            year=2024,
            winner_name="Winner One",
            user=self.user1,
            is_reviewed=True,
        )

    def test_award_badge_add_and_remove(self):
        """Test badge assignment and removal based on award status."""
        # Run command - should assign badge to user1
        call_command("owasp_update_badges")

        waspy_badge = Badge.objects.get(name=WASPY_BADGE_NAME)
        assert self.user1.badges.filter(pk=waspy_badge.pk).exists()
        assert not self.user2.badges.filter(pk=waspy_badge.pk).exists()

        # Make user1 no longer eligible by marking award as not reviewed
        Award.objects.filter(user=self.user1).update(is_reviewed=False)
        call_command("owasp_update_badges")

        # Refresh and check badge was removed
        self.user1.refresh_from_db()
        assert not self.user1.badges.filter(pk=waspy_badge.pk).exists()

    def test_repeated_runs(self):
        """Test that running command twice doesn't create duplicates."""
        call_command("owasp_update_badges")
        call_command("owasp_update_badges")  # Run twice

        waspy_badge = Badge.objects.get(name=WASPY_BADGE_NAME)
        # Should still have exactly one badge association
        assert self.user1.badges.filter(pk=waspy_badge.pk).count() == 1

    def test_badge_creation(self):
        """Test that badge is created if it doesn't exist."""
        # Ensure badge doesn't exist
        Badge.objects.filter(name=WASPY_BADGE_NAME).delete()

        call_command("owasp_update_badges")

        # Badge should be created
        assert Badge.objects.filter(name=WASPY_BADGE_NAME).exists()

        # User should have the badge
        waspy_badge = Badge.objects.get(name=WASPY_BADGE_NAME)
        assert self.user1.badges.filter(pk=waspy_badge.pk).exists()

    def test_only_reviewed_awards_get_badges(self):
        """Test that only reviewed awards result in badge assignment."""
        # Create not reviewed award
        Award.objects.create(
            category=Award.Category.WASPY,
            name="Another Award - Not Winner (2024)",
            description="",
            year=2024,
            winner_name="Not Winner",
            user=self.user2,
            is_reviewed=False,  # Not reviewed
        )

        call_command("owasp_update_badges")

        waspy_badge = Badge.objects.get(name=WASPY_BADGE_NAME)
        # Only user1 (reviewed award) should have badge
        assert self.user1.badges.filter(pk=waspy_badge.pk).exists()
        assert not self.user2.badges.filter(pk=waspy_badge.pk).exists()
