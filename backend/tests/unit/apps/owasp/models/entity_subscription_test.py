"""Tests for entity subscription model."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError

from apps.owasp.models.entity_subscription import MAX_ENTITY_SUBSCRIPTIONS, EntitySubscription


class TestEntitySubscription:
    """Test EntitySubscription model."""

    def test_str_representation_active(self):
        """Test string representation for active subscription."""
        sub = MagicMock(spec=EntitySubscription)
        sub.user = MagicMock()
        sub.name = "My Bundle"
        sub.frequency = EntitySubscription.Frequency.WEEKLY
        sub.is_active = True

        result = EntitySubscription.__str__(sub)
        assert result == f"{sub.user} (My Bundle, weekly, active)"

    def test_str_representation_inactive(self):
        """Test string representation for inactive subscription."""
        sub = MagicMock(spec=EntitySubscription)
        sub.user = MagicMock()
        sub.name = "Test"
        sub.frequency = EntitySubscription.Frequency.MONTHLY
        sub.is_active = False

        result = EntitySubscription.__str__(sub)
        assert result == f"{sub.user} (Test, monthly, inactive)"

    def test_frequency_choices(self):
        """Test frequency choices are correctly defined."""
        assert EntitySubscription.Frequency.WEEKLY == "weekly"
        assert EntitySubscription.Frequency.MONTHLY == "monthly"

    def test_unsubscribe_token_defaults(self):
        """Test that unsubscribe_token is a unique UUID for each instance."""
        first = EntitySubscription()
        second = EntitySubscription()

        assert isinstance(first.unsubscribe_token, uuid.UUID)
        assert isinstance(second.unsubscribe_token, uuid.UUID)
        assert first.unsubscribe_token != second.unsubscribe_token

    def test_max_entity_subscriptions_constant(self):
        """Test MAX_ENTITY_SUBSCRIPTIONS is defined."""
        assert MAX_ENTITY_SUBSCRIPTIONS == 5


class TestEntitySubscriptionClean:
    """Test EntitySubscription.clean method."""

    @patch("apps.owasp.models.entity_subscription.EntitySubscription.objects")
    def test_clean_success(self, mock_objects):
        """Test clean succeeds when under limit."""
        mock_objects.filter.return_value.count.return_value = 3
        sub = MagicMock(spec=EntitySubscription)
        sub.user_id = 1
        sub.is_active = True
        sub.pk = None
        sub.clean = EntitySubscription.clean.__get__(sub)

        # Should not raise exception
        sub.clean()

    @patch("apps.owasp.models.entity_subscription.EntitySubscription.objects")
    def test_clean_limit_reached(self, mock_objects):
        mock_objects.filter.return_value.count.return_value = MAX_ENTITY_SUBSCRIPTIONS
        sub = MagicMock(spec=EntitySubscription)
        sub.user_id = 1
        sub.is_active = True
        sub.pk = None
        sub.clean = EntitySubscription.clean.__get__(sub)

        error_msg = r"Maximum number of entity subscriptions reached\."
        with pytest.raises(ValidationError, match=error_msg):
            sub.clean()

    @patch("apps.owasp.models.entity_subscription.EntitySubscription.objects")
    def test_clean_skips_inactive(self, mock_objects):
        """Test clean skips limit check for inactive subscriptions."""
        sub = MagicMock(spec=EntitySubscription)
        sub.user_id = 1
        sub.is_active = False
        sub.clean = EntitySubscription.clean.__get__(sub)

        # Should not raise exception
        sub.clean()
        mock_objects.filter.assert_not_called()


class TestEntitySubscriptionCreate:
    """Test EntitySubscription.create class method."""

    @pytest.fixture(autouse=True)
    def _mock_transaction(self):
        """Disable transaction.atomic for tests."""
        with (
            patch("django.db.transaction.Atomic.__enter__", return_value=None),
            patch("django.db.transaction.Atomic.__exit__", return_value=False),
        ):
            yield

    @patch("apps.owasp.models.entity_subscription.EntitySubscription.objects")
    def test_create_success(self, mock_objects):
        """Test successful entity subscription creation."""
        user = MagicMock()
        mock_sub = MagicMock(spec=EntitySubscription)
        mock_objects.filter.return_value.count.return_value = 3
        mock_objects.create.return_value = mock_sub

        result = EntitySubscription.create(
            user=user,
            frequency="weekly",
            name="My bundle",
        )

        assert result == mock_sub

    @patch("apps.owasp.models.entity_subscription.EntitySubscription.objects")
    def test_create_limit_reached(self, mock_objects):
        """Test create returns None when entity limit reached."""
        user = MagicMock()
        mock_objects.filter.return_value.count.return_value = MAX_ENTITY_SUBSCRIPTIONS

        result = EntitySubscription.create(
            user=user,
            frequency="weekly",
        )

        assert result is None


class TestEntitySubscriptionUpdate:
    """Test EntitySubscription.update method."""

    def test_update_frequency(self):
        """Test updating frequency."""
        sub = MagicMock(spec=EntitySubscription)
        EntitySubscription.update(sub, frequency="monthly")

        assert sub.frequency == "monthly"
        sub.save.assert_called_once()

    def test_update_with_kwargs(self):
        """Test updating additional fields."""
        sub = MagicMock(spec=EntitySubscription)
        sub.name = "old"
        EntitySubscription.update(sub, name="new name")

        assert sub.name == "new name"
        sub.save.assert_called_once()

    def test_update_skips_none_values(self):
        """Test that None values are not applied."""
        sub = MagicMock(spec=EntitySubscription)
        sub.frequency = "weekly"
        EntitySubscription.update(sub, frequency=None)

        assert sub.frequency == "weekly"
        sub.save.assert_called_once()

    def test_update_skips_unknown_fields(self):
        """Test that unknown fields are not applied."""
        sub = MagicMock(spec=EntitySubscription)
        sub.frequency = "weekly"
        del sub.nonexistent_field
        EntitySubscription.update(sub, nonexistent_field="value")

        assert not hasattr(sub, "nonexistent_field")
        sub.save.assert_called_once()


class TestEntitySubscriptionSyncPreferences:
    """Test sync_preferences method."""

    def test_sync_creates_new_preferences(self):
        """Test sync creates new preferences when none exist."""
        sub = MagicMock(spec=EntitySubscription)
        sub.entity_preferences.all.return_value = []

        with patch(
            "apps.owasp.models.entity_subscription.EntitySubscriptionPreference",
        ) as mock_pref_cls:
            mock_pref_cls.objects.create.return_value = MagicMock()
            EntitySubscription.sync_preferences(
                sub,
                [
                    {
                        "entity_type": "project",
                        "entity_id": 1,
                        "include_issues": True,
                        "include_pull_requests": False,
                        "include_releases": True,
                    },
                ],
            )

            mock_pref_cls.objects.create.assert_called_once_with(
                subscription=sub,
                project_id=1,
                include_issues=True,
                include_pull_requests=False,
                include_releases=True,
            )

    def test_sync_updates_existing_preferences(self):
        """Test sync updates existing preferences when toggles change."""
        existing_pref = MagicMock()
        existing_pref.project_id = 1
        existing_pref.chapter_id = None
        existing_pref.committee_id = None
        existing_pref.include_issues = True
        existing_pref.include_pull_requests = True
        existing_pref.include_releases = True

        sub = MagicMock(spec=EntitySubscription)
        sub._preference_key = EntitySubscription._preference_key
        sub.entity_preferences.all.return_value = [existing_pref]

        EntitySubscription.sync_preferences(
            sub,
            [
                {
                    "entity_type": "project",
                    "entity_id": 1,
                    "include_issues": False,
                    "include_pull_requests": True,
                    "include_releases": True,
                },
            ],
        )

        assert existing_pref.include_issues is False
        existing_pref.save.assert_called_once()

    def test_sync_no_save_when_unchanged(self):
        """Test sync does not save when toggles are unchanged."""
        existing_pref = MagicMock()
        existing_pref.project_id = 1
        existing_pref.chapter_id = None
        existing_pref.committee_id = None
        existing_pref.include_issues = True
        existing_pref.include_pull_requests = True
        existing_pref.include_releases = True

        sub = MagicMock(spec=EntitySubscription)
        sub._preference_key = EntitySubscription._preference_key
        sub.entity_preferences.all.return_value = [existing_pref]

        EntitySubscription.sync_preferences(
            sub,
            [
                {
                    "entity_type": "project",
                    "entity_id": 1,
                    "include_issues": True,
                    "include_pull_requests": True,
                    "include_releases": True,
                },
            ],
        )

        existing_pref.save.assert_not_called()

    def test_sync_removes_old_preferences(self):
        """Test sync removes preferences no longer in input."""
        old_pref = MagicMock()
        old_pref.project_id = 99
        old_pref.chapter_id = None
        old_pref.committee_id = None

        sub = MagicMock(spec=EntitySubscription)
        sub.entity_preferences.all.return_value = [old_pref]

        EntitySubscription.sync_preferences(sub, [])

        old_pref.delete.assert_called_once()

    def test_sync_handles_chapter_entity(self):
        """Test sync creates chapter entity preference."""
        sub = MagicMock(spec=EntitySubscription)
        sub.entity_preferences.all.return_value = []

        with patch(
            "apps.owasp.models.entity_subscription.EntitySubscriptionPreference",
        ) as mock_pref_cls:
            EntitySubscription.sync_preferences(
                sub,
                [
                    {
                        "entity_type": "chapter",
                        "entity_id": 5,
                        "include_issues": True,
                        "include_pull_requests": True,
                        "include_releases": False,
                    },
                ],
            )

            mock_pref_cls.objects.create.assert_called_once_with(
                subscription=sub,
                chapter_id=5,
                include_issues=True,
                include_pull_requests=True,
                include_releases=False,
            )


class TestEntitySubscriptionPreferenceKey:
    """Test _preference_key static method."""

    def test_preference_key_project(self):
        """Test preference key for project."""
        pref = MagicMock()
        pref.project_id = 10
        pref.chapter_id = None
        pref.committee_id = None

        result = EntitySubscription._preference_key(pref)
        assert result == ("project", 10)

    def test_preference_key_chapter(self):
        """Test preference key for chapter."""
        pref = MagicMock()
        pref.project_id = None
        pref.chapter_id = 20
        pref.committee_id = None

        result = EntitySubscription._preference_key(pref)
        assert result == ("chapter", 20)

    def test_preference_key_committee(self):
        """Test preference key for committee."""
        pref = MagicMock()
        pref.project_id = None
        pref.chapter_id = None
        pref.committee_id = 30

        result = EntitySubscription._preference_key(pref)
        assert result == ("committee", 30)

    def test_preference_key_none_fallback(self):
        """Test preference key returns (None, None) when no entity set."""
        pref = MagicMock()
        pref.project_id = None
        pref.chapter_id = None
        pref.committee_id = None

        result = EntitySubscription._preference_key(pref)
        assert result == (None, None)
