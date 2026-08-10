"""Tests for snapshot subscription model."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.owasp.models.snapshot_subscription import MAX_SUBSCRIPTIONS, SnapshotSubscription


class TestSnapshotSubscription:
    """Test SnapshotSubscription model."""

    def test_str_representation_active(self):
        """Test string representation for active subscription."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.user = MagicMock()
        sub.name = "My Sub"
        sub.frequency = SnapshotSubscription.Frequency.WEEKLY
        sub.is_active = True

        result = SnapshotSubscription.__str__(sub)
        assert result == f"{sub.user} — My Sub (weekly, active)"

    def test_str_representation_inactive(self):
        """Test string representation for inactive subscription."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.user = MagicMock()
        sub.name = "Security"
        sub.frequency = SnapshotSubscription.Frequency.MONTHLY
        sub.is_active = False

        result = SnapshotSubscription.__str__(sub)
        assert result == f"{sub.user} — Security (monthly, inactive)"

    def test_str_representation_unnamed(self):
        """Test string representation for unnamed subscription."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.user = MagicMock()
        sub.name = ""
        sub.frequency = SnapshotSubscription.Frequency.WEEKLY
        sub.is_active = True

        result = SnapshotSubscription.__str__(sub)
        assert result == f"{sub.user} — Unnamed (weekly, active)"

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

    def test_max_subscriptions_constant(self):
        """Test MAX_SUBSCRIPTIONS is set to 5."""
        assert MAX_SUBSCRIPTIONS == 5


class TestSnapshotSubscriptionClean:
    """Test SnapshotSubscription.clean validation."""

    def test_clean_raises_when_all_toggles_off(self):
        """Test that clean raises ValidationError when all toggles are off."""
        sub = SnapshotSubscription(
            include_chapters=False,
            include_events=False,
            include_issues=False,
            include_posts=False,
            include_projects=False,
            include_pull_requests=False,
            include_releases=False,
            include_users=False,
        )

        with pytest.raises(ValidationError, match="At least one content toggle"):
            sub.clean()

    def test_clean_passes_with_one_toggle_on(self):
        """Test that clean passes when at least one toggle is on."""
        sub = SnapshotSubscription(
            include_chapters=False,
            include_events=False,
            include_issues=True,
            include_posts=False,
            include_projects=False,
            include_pull_requests=False,
            include_releases=False,
            include_users=False,
        )
        sub.clean()

    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_clean_raises_when_max_subscriptions_reached(self, mock_objects):
        """Test that clean raises ValidationError when max subscriptions reached."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.user_id = 1
        sub.user = MagicMock()
        sub.is_active = True
        sub.pk = None
        sub.include_chapters = True
        sub.include_events = True
        sub.include_issues = True
        sub.include_posts = True
        sub.include_projects = True
        sub.include_pull_requests = True
        sub.include_releases = True
        sub.include_users = True

        mock_objects.filter.return_value.count.return_value = MAX_SUBSCRIPTIONS

        with pytest.raises(ValidationError, match="Maximum number"):
            SnapshotSubscription.clean(sub)


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

    @patch("apps.owasp.models.snapshot_subscription.User.objects")
    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_create_success(self, mock_objects, mock_user_objects):
        """Test successful subscription creation."""
        user = MagicMock()
        user.pk = 1
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_objects.filter.return_value.count.return_value = 0
        mock_objects.create.return_value = mock_sub
        mock_select_qs = mock_user_objects.select_for_update.return_value.filter.return_value
        mock_select_qs.exists.return_value = True

        result = SnapshotSubscription.create(
            user=user,
            frequency="weekly",
            name="My Sub",
        )

        assert result == mock_sub
        mock_objects.create.assert_called_once()

    @patch("apps.owasp.models.snapshot_subscription.User.objects")
    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_create_returns_none_when_limit_reached(self, mock_objects, mock_user_objects):
        """Test create returns None when max subscriptions reached."""
        user = MagicMock()
        user.pk = 1
        mock_objects.filter.return_value.count.return_value = MAX_SUBSCRIPTIONS
        mock_select_qs = mock_user_objects.select_for_update.return_value.filter.return_value
        mock_select_qs.exists.return_value = True

        result = SnapshotSubscription.create(
            user=user,
            frequency="weekly",
        )

        assert result is None

    @patch("apps.owasp.models.snapshot_subscription.User.objects")
    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_create_with_name_and_toggles(self, mock_objects, mock_user_objects):
        """Test create passes name and toggles to objects.create."""
        user = MagicMock()
        user.pk = 1
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_objects.filter.return_value.count.return_value = 0
        mock_objects.create.return_value = mock_sub
        mock_select_qs = mock_user_objects.select_for_update.return_value.filter.return_value
        mock_select_qs.exists.return_value = True

        result = SnapshotSubscription.create(
            user=user,
            frequency="weekly",
            name="AI Security",
            include_chapters=False,
        )

        assert result == mock_sub
        mock_objects.create.assert_called_once_with(
            user=user,
            frequency="weekly",
            name="AI Security",
            include_chapters=False,
        )


class TestSnapshotSubscriptionUpdate:
    """Test SnapshotSubscription.update method."""

    def test_update_frequency(self):
        """Test updating frequency."""
        sub = MagicMock(spec=SnapshotSubscription)
        SnapshotSubscription.update(sub, frequency="monthly")

        assert sub.frequency == "monthly"
        sub.save.assert_called_once()

    def test_update_name(self):
        """Test updating name."""
        sub = MagicMock(spec=SnapshotSubscription)
        SnapshotSubscription.update(sub, name="New Name")

        assert sub.name == "New Name"
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


class TestSnapshotSubscriptionCleanEdgeCases:
    """Test SnapshotSubscription.clean edge cases for coverage."""

    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_clean_excludes_self_when_pk_exists(self, mock_objects):
        """Test that clean excludes the current instance when checking limit."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.user_id = 1
        sub.user = MagicMock()
        sub.is_active = True
        sub.pk = 42
        sub.include_chapters = True
        sub.include_events = True
        sub.include_issues = True
        sub.include_posts = True
        sub.include_projects = True
        sub.include_pull_requests = True
        sub.include_releases = True
        sub.include_users = True

        mock_qs = MagicMock()
        mock_qs.exclude.return_value = mock_qs
        mock_qs.count.return_value = 2
        mock_objects.filter.return_value = mock_qs

        SnapshotSubscription.clean(sub)

        mock_qs.exclude.assert_called_once_with(pk=42)

    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_clean_passes_when_under_max(self, mock_objects):
        """Test clean passes when active subscription count is under max."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.user_id = 1
        sub.user = MagicMock()
        sub.is_active = True
        sub.pk = None
        sub.include_chapters = True
        sub.include_events = True
        sub.include_issues = True
        sub.include_posts = True
        sub.include_projects = True
        sub.include_pull_requests = True
        sub.include_releases = True
        sub.include_users = True

        mock_objects.filter.return_value.count.return_value = MAX_SUBSCRIPTIONS - 1

        SnapshotSubscription.clean(sub)

        mock_objects.filter.assert_called_once_with(user=sub.user, is_active=True)


class TestSnapshotSubscriptionCreateEdgeCases:
    """Test SnapshotSubscription.create edge cases for coverage."""

    @pytest.fixture(autouse=True)
    def _mock_transaction(self):
        """Disable transaction.atomic for tests."""
        with (
            patch("django.db.transaction.Atomic.__enter__", return_value=None),
            patch("django.db.transaction.Atomic.__exit__", return_value=False),
        ):
            yield

    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_create_skips_select_for_update_when_no_user_pk(self, mock_objects):
        """Test create skips select_for_update when user has no pk."""
        user = MagicMock()
        user.pk = None
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_objects.filter.return_value.count.return_value = 0
        mock_objects.create.return_value = mock_sub

        result = SnapshotSubscription.create(user=user, frequency="weekly")

        assert result == mock_sub

    @patch("apps.owasp.models.snapshot_subscription.User.objects")
    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_create_returns_none_on_integrity_error(self, mock_objects, mock_user_objects):
        """Test create returns None when IntegrityError is raised."""
        user = MagicMock()
        user.pk = 1
        mock_objects.filter.return_value.count.return_value = 0
        mock_objects.create.side_effect = IntegrityError("duplicate")
        mock_select_qs = mock_user_objects.select_for_update.return_value.filter.return_value
        mock_select_qs.exists.return_value = True

        result = SnapshotSubscription.create(user=user, frequency="weekly")

        assert result is None


class TestSetM2mFields:
    """Test SnapshotSubscription.set_m2m_fields method."""

    @patch("apps.owasp.models.snapshot_subscription.Project.objects")
    def test_sets_projects(self, mock_project_objects):
        """Test setting subscribed projects."""
        sub = MagicMock(spec=SnapshotSubscription)
        mock_qs = MagicMock()
        mock_project_objects.filter.return_value = mock_qs

        SnapshotSubscription.set_m2m_fields(sub, project_ids=[1, 2])

        mock_project_objects.filter.assert_called_once_with(pk__in=[1, 2])
        sub.subscribed_projects.set.assert_called_once_with(mock_qs)

    @patch("apps.owasp.models.snapshot_subscription.Chapter.objects")
    def test_sets_chapters(self, mock_chapter_objects):
        """Test setting subscribed chapters."""
        sub = MagicMock(spec=SnapshotSubscription)
        mock_qs = MagicMock()
        mock_chapter_objects.filter.return_value = mock_qs

        SnapshotSubscription.set_m2m_fields(sub, chapter_ids=[3, 4])

        mock_chapter_objects.filter.assert_called_once_with(pk__in=[3, 4])
        sub.subscribed_chapters.set.assert_called_once_with(mock_qs)

    @patch("apps.owasp.models.snapshot_subscription.Committee.objects")
    def test_sets_committees(self, mock_committee_objects):
        """Test setting subscribed committees."""
        sub = MagicMock(spec=SnapshotSubscription)
        mock_qs = MagicMock()
        mock_committee_objects.filter.return_value = mock_qs

        SnapshotSubscription.set_m2m_fields(sub, committee_ids=[5])

        mock_committee_objects.filter.assert_called_once_with(pk__in=[5])
        sub.subscribed_committees.set.assert_called_once_with(mock_qs)

    def test_skips_all_when_none(self):
        """Test no M2M operations when all IDs are None."""
        sub = MagicMock(spec=SnapshotSubscription)

        SnapshotSubscription.set_m2m_fields(sub)

        sub.subscribed_projects.set.assert_not_called()
        sub.subscribed_chapters.set.assert_not_called()
        sub.subscribed_committees.set.assert_not_called()


class TestHasDuplicateSetup:
    """Test SnapshotSubscription.has_duplicate_setup method."""

    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_returns_false_when_no_matching_subs(self, mock_objects):
        """Test returns False when no other subs match frequency+toggles."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.pk = 1
        sub.user = MagicMock()
        sub.frequency = "weekly"
        sub.include_chapters = True
        sub.include_events = True
        sub.include_issues = True
        sub.include_posts = True
        sub.include_projects = True
        sub.include_pull_requests = True
        sub.include_releases = True
        sub.include_users = True

        mock_qs = MagicMock()
        mock_qs.exclude.return_value = mock_qs
        mock_qs.prefetch_related.return_value = mock_qs
        mock_qs.exists.return_value = False
        mock_objects.filter.return_value = mock_qs

        result = SnapshotSubscription.has_duplicate_setup(sub)

        assert result is False

    @patch("apps.owasp.models.snapshot_subscription.SnapshotSubscription.objects")
    def test_returns_true_when_duplicate_found(self, mock_objects):
        """Test returns True when another sub has exact same setup."""
        sub = MagicMock(spec=SnapshotSubscription)
        sub.pk = 1
        sub.user = MagicMock()
        sub.frequency = "weekly"
        sub.include_chapters = True
        sub.include_events = True
        sub.include_issues = True
        sub.include_posts = True
        sub.include_projects = True
        sub.include_pull_requests = True
        sub.include_releases = True
        sub.include_users = True
        sub.subscribed_projects.values_list.return_value = [10]
        sub.subscribed_chapters.values_list.return_value = [20]
        sub.subscribed_committees.values_list.return_value = []

        mock_project = MagicMock(pk=10)
        mock_chapter = MagicMock(pk=20)
        other = MagicMock()
        other.subscribed_projects.all.return_value = [mock_project]
        other.subscribed_chapters.all.return_value = [mock_chapter]
        other.subscribed_committees.all.return_value = []

        mock_qs = MagicMock()
        mock_qs.exclude.return_value = mock_qs
        mock_qs.prefetch_related.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = MagicMock(return_value=iter([other]))
        mock_objects.filter.return_value = mock_qs

        result = SnapshotSubscription.has_duplicate_setup(sub)

        assert result is True
