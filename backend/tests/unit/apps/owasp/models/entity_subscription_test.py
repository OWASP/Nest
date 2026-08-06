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
        sub.entity = MagicMock()
        sub.frequency = EntitySubscription.Frequency.WEEKLY
        sub.is_active = True

        result = EntitySubscription.__str__(sub)
        assert "weekly" in result
        assert "active" in result

    def test_str_representation_inactive(self):
        """Test string representation for inactive subscription."""
        sub = MagicMock(spec=EntitySubscription)
        sub.entity = MagicMock()
        sub.frequency = EntitySubscription.Frequency.MONTHLY
        sub.is_active = False

        result = EntitySubscription.__str__(sub)
        assert "monthly" in result
        assert "inactive" in result

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


class TestEntitySubscriptionEntity:
    """Test entity property and entity_type property."""

    def test_entity_returns_chapter(self):
        """Test entity property returns chapter when set."""
        sub = MagicMock(spec=EntitySubscription)
        sub.chapter = MagicMock()
        sub.committee = None
        sub.project = None

        result = EntitySubscription.entity.fget(sub)
        assert result == sub.chapter

    def test_entity_returns_committee(self):
        """Test entity property returns committee when set."""
        sub = MagicMock(spec=EntitySubscription)
        sub.chapter = None
        sub.committee = MagicMock()
        sub.project = None

        result = EntitySubscription.entity.fget(sub)
        assert result == sub.committee

    def test_entity_returns_project(self):
        """Test entity property returns project when set."""
        sub = MagicMock(spec=EntitySubscription)
        sub.chapter = None
        sub.committee = None
        sub.project = MagicMock()

        result = EntitySubscription.entity.fget(sub)
        assert result == sub.project

    def test_entity_type_chapter(self):
        """Test entity_type returns chapter."""
        sub = MagicMock(spec=EntitySubscription)
        sub.chapter_id = 1
        sub.committee_id = None
        sub.project_id = None

        result = EntitySubscription.entity_type.fget(sub)
        assert result == "chapter"

    def test_entity_type_committee(self):
        """Test entity_type returns committee."""
        sub = MagicMock(spec=EntitySubscription)
        sub.chapter_id = None
        sub.committee_id = 2
        sub.project_id = None

        result = EntitySubscription.entity_type.fget(sub)
        assert result == "committee"

    def test_entity_type_project(self):
        """Test entity_type returns project."""
        sub = MagicMock(spec=EntitySubscription)
        sub.chapter_id = None
        sub.committee_id = None
        sub.project_id = 3

        result = EntitySubscription.entity_type.fget(sub)
        assert result == "project"

    def test_entity_type_none(self):
        """Test entity_type returns None when no entity set."""
        sub = MagicMock(spec=EntitySubscription)
        sub.chapter_id = None
        sub.committee_id = None
        sub.project_id = None

        result = EntitySubscription.entity_type.fget(sub)
        assert result is None


class TestEntitySubscriptionClean:
    """Test EntitySubscription.clean method."""

    @patch("apps.owasp.models.entity_subscription.EntitySubscription.objects")
    def test_clean_success(self, mock_objects):
        """Test clean succeeds when under limit."""
        filter_mock = MagicMock()
        filter_mock.exists.return_value = False
        filter_mock.count.return_value = 3
        mock_objects.filter.return_value = filter_mock
        sub = MagicMock(spec=EntitySubscription)
        sub.user_id = 1
        sub.is_active = True
        sub.pk = None
        sub.project_id = 10
        sub.chapter_id = None
        sub.committee_id = None
        sub.clean = EntitySubscription.clean.__get__(sub)
        sub.clean()

    @patch("apps.owasp.models.entity_subscription.EntitySubscription.objects")
    def test_clean_limit_reached(self, mock_objects):
        filter_mock = MagicMock()
        filter_mock.exists.return_value = False
        filter_mock.count.return_value = MAX_ENTITY_SUBSCRIPTIONS
        mock_objects.filter.return_value = filter_mock
        sub = MagicMock(spec=EntitySubscription)
        sub.user_id = 1
        sub.is_active = True
        sub.pk = None
        sub.project_id = 10
        sub.chapter_id = None
        sub.committee_id = None
        sub.clean = EntitySubscription.clean.__get__(sub)

        error_msg = r"Maximum number of entity subscriptions reached\."
        with pytest.raises(ValidationError, match=error_msg):
            sub.clean()

    @patch("apps.owasp.models.entity_subscription.EntitySubscription.objects")
    def test_clean_skips_inactive(self, mock_objects):
        """Test clean skips limit check for inactive subscriptions."""
        filter_mock = MagicMock()
        filter_mock.exists.return_value = False
        mock_objects.filter.return_value = filter_mock
        sub = MagicMock(spec=EntitySubscription)
        sub.user_id = 1
        sub.is_active = False
        sub.pk = None
        sub.project_id = 10
        sub.chapter_id = None
        sub.committee_id = None
        sub.clean = EntitySubscription.clean.__get__(sub)
        sub.clean()

    @patch("apps.owasp.models.entity_subscription.EntitySubscription.objects")
    def test_clean_existing_subscription_at_limit(self, mock_objects):
        """Test clean succeeds for existing subscription when at limit."""
        filter_mock = MagicMock()
        filter_mock.exists.return_value = False
        filter_mock.exclude.return_value.exists.return_value = False
        filter_mock.exclude.return_value.count.return_value = MAX_ENTITY_SUBSCRIPTIONS - 1
        mock_objects.filter.return_value = filter_mock
        sub = MagicMock(spec=EntitySubscription)
        sub.user_id = 1
        sub.is_active = True
        sub.pk = 42
        sub.project_id = 10
        sub.chapter_id = None
        sub.committee_id = None
        sub.clean = EntitySubscription.clean.__get__(sub)
        sub.clean()

    @patch("apps.owasp.models.entity_subscription.EntitySubscription.objects")
    def test_clean_duplicate_subscription(self, mock_objects):
        """Test clean fails when duplicate entity subscription exists."""
        filter_mock = MagicMock()
        filter_mock.exists.return_value = True
        mock_objects.filter.return_value = filter_mock
        sub = MagicMock(spec=EntitySubscription)
        sub.user_id = 1
        sub.is_active = True
        sub.pk = None
        sub.project_id = 10
        sub.chapter_id = None
        sub.committee_id = None
        sub.clean = EntitySubscription.clean.__get__(sub)

        with pytest.raises(ValidationError, match=r"already subscribed"):
            sub.clean()

    def test_clean_no_entity_set(self):
        """Test clean fails when no entity is set."""
        sub = MagicMock(spec=EntitySubscription)
        sub.project_id = None
        sub.chapter_id = None
        sub.committee_id = None
        sub.clean = EntitySubscription.clean.__get__(sub)

        with pytest.raises(ValidationError, match=r"must select exactly one"):
            sub.clean()

    def test_clean_multiple_entities_set(self):
        """Test clean fails when multiple entities are set."""
        sub = MagicMock(spec=EntitySubscription)
        sub.project_id = 10
        sub.chapter_id = 20
        sub.committee_id = None
        sub.clean = EntitySubscription.clean.__get__(sub)

        with pytest.raises(ValidationError, match=r"only subscribe to one entity"):
            sub.clean()


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

    @patch("apps.owasp.models.entity_subscription.User.objects")
    @patch("apps.owasp.models.entity_subscription.EntitySubscription.objects")
    def test_create_success(self, mock_objects, mock_user_objects):
        """Test successful entity subscription creation."""
        user = MagicMock()
        user.pk = 1
        mock_sub = MagicMock(spec=EntitySubscription)
        mock_objects.filter.return_value.count.return_value = 3
        mock_objects.create.return_value = mock_sub

        result = EntitySubscription.create(
            user=user,
            frequency="weekly",
            entity_type="project",
            entity_id=10,
        )

        assert result == mock_sub
        mock_objects.create.assert_called_once_with(
            user=user,
            frequency="weekly",
            project_id=10,
        )

    @patch("apps.owasp.models.entity_subscription.User.objects")
    @patch("apps.owasp.models.entity_subscription.EntitySubscription.objects")
    def test_create_chapter(self, mock_objects, mock_user_objects):
        """Test creating a chapter subscription."""
        user = MagicMock()
        user.pk = 1
        mock_sub = MagicMock(spec=EntitySubscription)
        mock_objects.filter.return_value.count.return_value = 0
        mock_objects.create.return_value = mock_sub

        result = EntitySubscription.create(
            user=user,
            frequency="monthly",
            entity_type="chapter",
            entity_id=5,
        )

        assert result == mock_sub
        mock_objects.create.assert_called_once_with(
            user=user,
            frequency="monthly",
            chapter_id=5,
        )

    @patch("apps.owasp.models.entity_subscription.User.objects")
    @patch("apps.owasp.models.entity_subscription.EntitySubscription.objects")
    def test_create_limit_reached(self, mock_objects, mock_user_objects):
        """Test create returns None when entity limit reached."""
        user = MagicMock()
        user.pk = 1
        mock_objects.filter.return_value.count.return_value = MAX_ENTITY_SUBSCRIPTIONS

        result = EntitySubscription.create(
            user=user,
            frequency="weekly",
            entity_type="project",
            entity_id=1,
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

    def test_update_skips_none_values(self):
        """Test that None values are not applied."""
        sub = MagicMock(spec=EntitySubscription)
        sub.frequency = "weekly"
        EntitySubscription.update(sub, frequency=None)

        assert sub.frequency == "weekly"
        sub.save.assert_called_once()

    def test_update_calls_full_clean(self):
        """Test update calls full_clean before saving."""
        sub = MagicMock(spec=EntitySubscription)
        EntitySubscription.update(sub, frequency="monthly")

        sub.full_clean.assert_called_once()
        sub.save.assert_called_once()


class TestEntitySubscriptionMeta:
    """Test EntitySubscription Meta configuration."""

    def test_constraints_exist(self):
        """Test constraints are defined on the model."""
        constraint_names = {c.name for c in EntitySubscription._meta.constraints}
        assert "entity_sub_exactly_one_entity" in constraint_names
        assert "unique_user_project_subscription" in constraint_names
        assert "unique_user_chapter_subscription" in constraint_names
        assert "unique_user_committee_subscription" in constraint_names

    def test_db_table(self):
        """Test database table name."""
        assert EntitySubscription._meta.db_table == "owasp_entity_subscriptions"
