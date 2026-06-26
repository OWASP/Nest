"""Tests for snapshot subscription model."""

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from apps.owasp.models.snapshot_subscription import SnapshotSubscription


class TestSnapshotSubscription(SimpleTestCase):
    """Test SnapshotSubscription model."""

    def test_str_representation_active(self):
        """Test string representation for active subscription."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.user = MagicMock()
        sub.frequency = SnapshotSubscription.Frequency.WEEKLY
        sub.is_active = True

        result = SnapshotSubscription.__str__(sub)
        assert result == f"{sub.user} (weekly, active)"

    def test_str_representation_inactive(self):
        """Test string representation for inactive subscription."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.user = MagicMock()
        sub.frequency = SnapshotSubscription.Frequency.MONTHLY
        sub.is_active = False

        result = SnapshotSubscription.__str__(sub)
        assert result == f"{sub.user} (monthly, inactive)"

    def test_content_preferences_all_defaults(self):
        """Test that content_preferences returns all True by default."""
        sub = SnapshotSubscription()
        prefs = sub.content_preferences
        assert prefs == {
            "chapters": True,
            "events": True,
            "issues": True,
            "posts": True,
            "projects": True,
            "pull_requests": True,
            "releases": True,
            "users": True,
        }

    def test_content_preferences_custom(self):
        """Test content_preferences with custom values."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.include_chapters = False
        sub.include_events = True
        sub.include_issues = True
        sub.include_posts = False
        sub.include_projects = False
        sub.include_pull_requests = True
        sub.include_releases = True
        sub.include_users = True

        prefs = SnapshotSubscription.content_preferences.fget(sub)
        assert prefs == {
            "chapters": False,
            "events": True,
            "issues": True,
            "posts": False,
            "projects": False,
            "pull_requests": True,
            "releases": True,
            "users": True,
        }

    def test_frequency_choices(self):
        """Test frequency choices are correctly defined."""
        assert SnapshotSubscription.Frequency.WEEKLY == "weekly"
        assert SnapshotSubscription.Frequency.MONTHLY == "monthly"
