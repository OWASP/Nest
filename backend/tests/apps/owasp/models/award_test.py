"""Tests for Award model."""

from django.test import TestCase

from apps.github.models.user import User
from apps.owasp.models.award import Award


class AwardModelTest(TestCase):
    """Test cases for Award model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create(
            login="testuser",
            name="Test User",
            email="test@example.com",
            created_at="2020-01-01T00:00:00Z",
            updated_at="2020-01-01T00:00:00Z",
        )

    def test_create_award(self):
        """Test creating an award."""
        award = Award.objects.create(
            name="Test Award",
            category="WASPY",
            year=2024,
            award_type="award",
            winner_name="Test User",
            user=self.user,
        )

        assert award.name == "Test Award"
        assert award.category == "WASPY"
        assert award.year == 2024
        assert award.winner_name == "Test User"
        assert award.user == self.user

    def test_get_waspy_award_winners(self):
        """Test getting WASPY award winners."""
        Award.objects.create(
            name="Test Award",
            category="WASPY",
            year=2024,
            award_type="award",
            winner_name="Test User",
            user=self.user,
        )

        winners = Award.get_waspy_award_winners()
        assert self.user in winners

    def test_get_user_waspy_awards(self):
        """Test getting WASPY awards for a user."""
        award = Award.objects.create(
            name="Test Award",
            category="WASPY",
            year=2024,
            award_type="award",
            winner_name="Test User",
            user=self.user,
        )

        user_awards = Award.get_user_waspy_awards(self.user)
        assert award in user_awards
