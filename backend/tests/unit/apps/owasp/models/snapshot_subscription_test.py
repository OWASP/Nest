"""Tests for snapshot subscription model."""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from apps.owasp.models.snapshot_subscription import SnapshotSubscription


class TestSnapshotSubscription:
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
        sub.include_issues = False
        sub.include_posts = False
        sub.include_projects = True
        sub.include_pull_requests = False
        sub.include_releases = True
        sub.include_users = True

        prefs = SnapshotSubscription.content_preferences.fget(sub)
        assert prefs == {
            "chapters": False,
            "events": True,
            "issues": False,
            "posts": False,
            "projects": True,
            "pull_requests": False,
            "releases": True,
            "users": True,
        }

    def test_frequency_choices(self):
        """Test frequency choices are correctly defined."""
        assert SnapshotSubscription.Frequency.WEEKLY == "weekly"
        assert SnapshotSubscription.Frequency.MONTHLY == "monthly"

    def test_unsubscribe_token_defaults(self):
        """Test that unsubscribe_token is a unique UUID for each instance."""
        first = SnapshotSubscription()
        second = SnapshotSubscription()

        assert isinstance(first.unsubscribe_token, uuid.UUID)
        assert isinstance(second.unsubscribe_token, uuid.UUID)
        assert first.unsubscribe_token != second.unsubscribe_token


class TestSnapshotSubscriptionCreate:
    """Test SnapshotSubscription.create class method."""

    @pytest.fixture(autouse=True)
    def _mock_transaction(self):
        """Disable transaction.atomic for tests."""
        with (
            patch("django.db.transaction.Atomic.__enter__", return_value=None),
            patch("django.db.transaction.Atomic.__exit__", return_value=False),
        ):
            yield

    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_create_success(self, mock_objects):
        """Test successful subscription creation."""
        user = MagicMock()
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_objects.filter.return_value.first.return_value = None
        mock_objects.create.return_value = mock_sub

        result = SnapshotSubscription.create(
            user=user,
            frequency="weekly",
        )

        assert result == mock_sub
        mock_objects.create.assert_called_once()

    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_create_already_active(self, mock_objects):
        """Test create returns None when active subscription exists."""
        user = MagicMock()
        existing = MagicMock(spec=SnapshotSubscription)
        existing.is_active = True
        mock_objects.filter.return_value.first.return_value = existing

        result = SnapshotSubscription.create(
            user=user,
            frequency="weekly",
        )

        assert result is None

    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_create_reactivates_inactive(self, mock_objects):
        """Test create reactivates an inactive subscription."""
        user = MagicMock()
        existing = MagicMock(spec=SnapshotSubscription)
        existing.is_active = False
        mock_objects.filter.return_value.first.return_value = existing

        result = SnapshotSubscription.create(
            user=user,
            frequency="monthly",
        )

        assert result == existing
        assert existing.is_active is True
        assert existing.frequency == "monthly"
        existing.save.assert_called_once()


class TestSnapshotSubscriptionUpdate:
    """Test SnapshotSubscription.update method."""

    def test_update_frequency(self):
        """Test updating frequency."""
        sub = MagicMock(spec=SnapshotSubscription)
        SnapshotSubscription.update(sub, frequency="monthly")

        assert sub.frequency == "monthly"
        sub.save.assert_called_once()

    def test_update_with_kwargs(self):
        """Test updating additional fields."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.include_chapters = True
        SnapshotSubscription.update(sub, include_chapters=False)

        assert sub.include_chapters is False
        sub.save.assert_called_once()

    def test_update_skips_none_values(self):
        """Test that None values are not applied."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.frequency = "weekly"
        SnapshotSubscription.update(sub, frequency=None)

        assert sub.frequency == "weekly"
        sub.save.assert_called_once()

    def test_update_skips_unknown_fields(self):
        """Test that unknown fields are not applied."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.frequency = "weekly"
        del sub.nonexistent_field
        SnapshotSubscription.update(sub, nonexistent_field="value")

        assert not hasattr(sub, "nonexistent_field")
        sub.save.assert_called_once()


class TestSnapshotSubscriptionCreateReactivationKwargs:
    """Test reactivation with kwargs in create method."""

    @pytest.fixture(autouse=True)
    def _mock_transaction(self):
        """Disable transaction.atomic for tests."""
        with (
            patch("django.db.transaction.Atomic.__enter__", return_value=None),
            patch("django.db.transaction.Atomic.__exit__", return_value=False),
        ):
            yield

    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_create_reactivates_with_kwargs(self, mock_objects):
        """Test reactivation applies additional kwargs like content toggles."""
        user = MagicMock()
        existing = MagicMock(spec=SnapshotSubscription)
        existing.is_active = False
        mock_objects.filter.return_value.first.return_value = existing

        result = SnapshotSubscription.create(
            user=user,
            frequency="weekly",
            include_chapters=False,
            include_events=False,
        )

        assert result == existing
        assert existing.is_active is True
        assert existing.include_chapters is False
        assert existing.include_events is False
        existing.save.assert_called_once()

    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_create_reactivate_skips_none_kwargs(self, mock_objects):
        """Test reactivation skips None-valued kwargs."""
        user = MagicMock()
        existing = MagicMock(spec=SnapshotSubscription)
        existing.is_active = False
        existing.include_chapters = True
        mock_objects.filter.return_value.first.return_value = existing

        result = SnapshotSubscription.create(
            user=user,
            frequency="weekly",
            include_chapters=None,
        )

        assert result == existing
        assert existing.include_chapters is True
