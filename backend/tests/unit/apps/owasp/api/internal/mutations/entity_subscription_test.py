"""Tests for entity subscription GraphQL mutations."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.owasp.api.internal.mutations.entity_subscription import (
    CreateEntitySubscriptionInput,
    EntityPreferenceInput,
    EntitySubscriptionMutations,
    EntitySubscriptionResult,
    UpdateEntitySubscriptionInput,
)
from apps.owasp.models.entity_subscription import EntitySubscription

MOCK_TOKEN = "mock-unsubscribe-token"  # noqa: S105


@pytest.fixture(autouse=True)
def _mock_transaction_atomic():
    """Disable transaction.atomic decorator for all tests."""
    with (
        patch("django.db.transaction.Atomic.__enter__", return_value=None),
        patch("django.db.transaction.Atomic.__exit__", return_value=False),
    ):
        yield


def mock_info() -> MagicMock:
    """Return a mocked Info object."""
    info = MagicMock()
    info.context = MagicMock()
    info.context.request = MagicMock()
    info.context.request.user = MagicMock()
    info.context.request.user.is_authenticated = True
    return info


class TestEntitySubscriptionResult:
    """Test cases for EntitySubscriptionResult."""

    def test_result_ok(self):
        result = EntitySubscriptionResult(ok=True, message="Success")
        assert result.ok
        assert result.message == "Success"

    def test_result_not_ok(self):
        result = EntitySubscriptionResult(ok=False, message="Failed")
        assert not result.ok
        assert result.message == "Failed"


class TestCreateEntitySubscription:
    """Test cases for createEntitySubscription mutation."""

    @pytest.fixture
    def mutations(self):
        return EntitySubscriptionMutations()

    def test_invalid_frequency(self, mutations):
        """Test create fails with invalid frequency."""
        info = mock_info()
        input_data = CreateEntitySubscriptionInput(
            frequency="daily",
            entity_preferences=[
                EntityPreferenceInput(entity_type="project", entity_id=10),
            ],
        )
        result = mutations.create_entity_subscription(info, input_data=input_data)
        assert not result.ok

    def test_invalid_entity_type(self, mutations):
        """Test create fails with invalid entity type."""
        info = mock_info()
        input_data = CreateEntitySubscriptionInput(
            entity_preferences=[
                EntityPreferenceInput(entity_type="invalid", entity_id=10),
            ],
        )
        result = mutations.create_entity_subscription(info, input_data=input_data)
        assert not result.ok

    def test_empty_preferences(self, mutations):
        """Test create fails with empty preferences."""
        info = mock_info()
        input_data = CreateEntitySubscriptionInput(entity_preferences=[])
        result = mutations.create_entity_subscription(info, input_data=input_data)
        assert not result.ok

    def test_duplicate_entities(self, mutations):
        """Test create fails with duplicate entities."""
        info = mock_info()
        input_data = CreateEntitySubscriptionInput(
            entity_preferences=[
                EntityPreferenceInput(entity_type="project", entity_id=10),
                EntityPreferenceInput(entity_type="project", entity_id=10),
            ],
        )
        result = mutations.create_entity_subscription(info, input_data=input_data)
        assert not result.ok

    def test_too_many_preferences(self, mutations):
        """Test create fails with more than 50 preferences."""
        info = mock_info()
        input_data = CreateEntitySubscriptionInput(
            entity_preferences=[
                EntityPreferenceInput(entity_type="project", entity_id=i) for i in range(1, 52)
            ],
        )
        result = mutations.create_entity_subscription(info, input_data=input_data)
        assert not result.ok
        assert "at most 50 preferences" in result.message

    def test_invalid_entity_id(self, mutations):
        """Test create fails with invalid entity ID."""
        info = mock_info()
        input_data = CreateEntitySubscriptionInput(
            entity_preferences=[
                EntityPreferenceInput(entity_type="project", entity_id=-1),
            ],
        )
        result = mutations.create_entity_subscription(info, input_data=input_data)
        assert not result.ok
        assert "positive integer" in result.message

    def test_invalid_name(self, mutations):
        """Test create fails with too long name."""
        info = mock_info()
        input_data = CreateEntitySubscriptionInput(
            name="a" * 101,
            entity_preferences=[
                EntityPreferenceInput(entity_type="project", entity_id=1),
            ],
        )
        result = mutations.create_entity_subscription(info, input_data=input_data)
        assert not result.ok
        assert "100 characters or fewer" in result.message

    @patch("apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.create")
    def test_create_integrity_error(self, mock_create, mutations):
        """Test create handles IntegrityError."""
        info = mock_info()
        input_data = CreateEntitySubscriptionInput(
            entity_preferences=[
                EntityPreferenceInput(entity_type="project", entity_id=10),
            ],
        )
        mock_create.side_effect = IntegrityError("Database error")
        result = mutations.create_entity_subscription(info, input_data=input_data)
        assert not result.ok
        assert "Failed to create subscription" in result.message

    @patch("apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.create")
    def test_create_validation_error(self, mock_create, mutations):
        """Test create handles ValidationError."""
        info = mock_info()
        input_data = CreateEntitySubscriptionInput(
            entity_preferences=[
                EntityPreferenceInput(entity_type="project", entity_id=10),
            ],
        )
        mock_create.side_effect = ValidationError("Custom validation error")
        result = mutations.create_entity_subscription(info, input_data=input_data)
        assert not result.ok
        assert "Custom validation error" in result.message

    @patch("apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.create")
    def test_create_success(self, mock_create, mutations):
        """Test successful entity subscription creation."""
        info = mock_info()
        input_data = CreateEntitySubscriptionInput(
            frequency="weekly",
            entity_preferences=[
                EntityPreferenceInput(entity_type="project", entity_id=10),
            ],
        )
        mock_sub = MagicMock(spec=EntitySubscription)
        mock_create.return_value = mock_sub

        result = mutations.create_entity_subscription(info, input_data=input_data)

        assert result.ok
        mock_sub.sync_preferences.assert_called_once()

    @patch("apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.create")
    def test_create_limit_reached(self, mock_create, mutations):
        """Test create fails when entity limit reached."""
        info = mock_info()
        input_data = CreateEntitySubscriptionInput(
            frequency="weekly",
            entity_preferences=[
                EntityPreferenceInput(entity_type="project", entity_id=10),
            ],
        )
        mock_create.return_value = None

        result = mutations.create_entity_subscription(info, input_data=input_data)

        assert not result.ok
        assert result.message == "Maximum number of entity subscriptions reached."


class TestUpdateEntitySubscription:
    """Test cases for updateEntitySubscription mutation."""

    @pytest.fixture
    def mutations(self):
        return EntitySubscriptionMutations()

    def test_not_found(self, mutations):
        """Test update fails when subscription doesn't exist."""
        info = mock_info()
        input_data = UpdateEntitySubscriptionInput()
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.side_effect = EntitySubscription.DoesNotExist
            result = mutations.update_entity_subscription(
                info, subscription_id=999, input_data=input_data
            )
            assert not result.ok
            assert result.message == "Subscription not found."

    def test_invalid_frequency(self, mutations):
        """Test update fails with invalid frequency."""
        info = mock_info()
        input_data = UpdateEntitySubscriptionInput(frequency="daily")
        mock_sub = MagicMock(spec=EntitySubscription)
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.update_entity_subscription(
                info, subscription_id=1, input_data=input_data
            )
            assert not result.ok

    def test_invalid_name(self, mutations):
        """Test update fails with too long name."""
        info = mock_info()
        input_data = UpdateEntitySubscriptionInput(name="a" * 101)
        mock_sub = MagicMock(spec=EntitySubscription)
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.update_entity_subscription(
                info, subscription_id=1, input_data=input_data
            )
            assert not result.ok
            assert "100 characters or fewer" in result.message

    def test_invalid_entity_preferences(self, mutations):
        """Test update fails with invalid preferences."""
        info = mock_info()
        input_data = UpdateEntitySubscriptionInput(
            entity_preferences=[
                EntityPreferenceInput(entity_type="invalid", entity_id=10),
            ],
        )
        mock_sub = MagicMock(spec=EntitySubscription)
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.update_entity_subscription(
                info, subscription_id=1, input_data=input_data
            )
            assert not result.ok

    def test_update_integrity_error(self, mutations):
        """Test update handles IntegrityError."""
        info = mock_info()
        input_data = UpdateEntitySubscriptionInput(frequency="monthly")
        mock_sub = MagicMock(spec=EntitySubscription)
        mock_sub.update.side_effect = IntegrityError("Database error")
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.update_entity_subscription(
                info, subscription_id=1, input_data=input_data
            )
            assert not result.ok
            assert "Failed to update subscription" in result.message

    def test_success(self, mutations):
        """Test successful subscription update."""
        info = mock_info()
        input_data = UpdateEntitySubscriptionInput(frequency="monthly")
        mock_sub = MagicMock(spec=EntitySubscription)
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.update_entity_subscription(
                info, subscription_id=1, input_data=input_data
            )
            assert result.ok
            mock_sub.update.assert_called_once()

    def test_success_with_entity_preferences(self, mutations):
        """Test successful update with entity preferences."""
        info = mock_info()
        pref = EntityPreferenceInput(entity_type="project", entity_id=20)
        input_data = UpdateEntitySubscriptionInput(entity_preferences=[pref])
        mock_sub = MagicMock(spec=EntitySubscription)
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.update_entity_subscription(
                info, subscription_id=1, input_data=input_data
            )
            assert result.ok
            mock_sub.sync_preferences.assert_called_once()


class TestCancelEntitySubscription:
    """Test cases for cancelEntitySubscription mutation."""

    @pytest.fixture
    def mutations(self):
        return EntitySubscriptionMutations()

    def test_not_found(self, mutations):
        """Test cancel fails when subscription doesn't exist."""
        info = mock_info()
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.side_effect = EntitySubscription.DoesNotExist
            result = mutations.cancel_entity_subscription(info, subscription_id=999)
            assert not result.ok

    def test_success(self, mutations):
        """Test successful subscription cancellation (soft deactivate)."""
        info = mock_info()
        mock_sub = MagicMock(spec=EntitySubscription)
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.cancel_entity_subscription(info, subscription_id=1)
            assert result.ok
            assert mock_sub.is_active is False
            mock_sub.save.assert_called_once()


class TestDeleteEntitySubscription:
    """Test cases for deleteEntitySubscription mutation."""

    @pytest.fixture
    def mutations(self):
        return EntitySubscriptionMutations()

    def test_not_found(self, mutations):
        """Test delete fails when subscription doesn't exist."""
        info = mock_info()
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.side_effect = EntitySubscription.DoesNotExist
            result = mutations.delete_entity_subscription(info, subscription_id=999)
            assert not result.ok

    def test_success(self, mutations):
        """Test successful subscription hard delete."""
        info = mock_info()
        mock_sub = MagicMock(spec=EntitySubscription)
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.delete_entity_subscription(info, subscription_id=1)
            assert result.ok
            mock_sub.delete.assert_called_once()


class TestReactivateEntitySubscription:
    """Test cases for reactivateEntitySubscription mutation."""

    @pytest.fixture
    def mutations(self):
        return EntitySubscriptionMutations()

    def test_not_found(self, mutations):
        """Test reactivate fails when subscription doesn't exist."""
        info = mock_info()
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.side_effect = EntitySubscription.DoesNotExist
            result = mutations.reactivate_entity_subscription(info, subscription_id=999)
            assert not result.ok

    def test_already_active(self, mutations):
        """Test reactivate fails when subscription is already active."""
        info = mock_info()
        mock_sub = MagicMock(spec=EntitySubscription)
        mock_sub.is_active = True
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.reactivate_entity_subscription(info, subscription_id=1)
            assert not result.ok

    def test_success(self, mutations):
        """Test successful subscription reactivation."""
        info = mock_info()
        mock_sub = MagicMock(spec=EntitySubscription)
        mock_sub.is_active = False
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            mock_objects.filter.return_value.count.return_value = 0
            result = mutations.reactivate_entity_subscription(info, subscription_id=1)
            assert result.ok
            assert mock_sub.is_active is True
            mock_sub.save.assert_called_once()


class TestUnsubscribeEntityByToken:
    """Test cases for unsubscribeEntityByToken mutation."""

    @pytest.fixture
    def mutations(self):
        return EntitySubscriptionMutations()

    def test_invalid_token(self, mutations):
        """Test unsubscribe fails with invalid token."""
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.side_effect = EntitySubscription.DoesNotExist
            result = mutations.unsubscribe_entity_by_token(token=str(uuid.uuid4()))
            assert not result.ok

    def test_malformed_token(self, mutations):
        """Test unsubscribe fails with malformed token."""
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.side_effect = ValidationError("Invalid UUID")
            result = mutations.unsubscribe_entity_by_token(token=MOCK_TOKEN)
            assert not result.ok

    def test_already_inactive(self, mutations):
        """Test unsubscribe fails when already inactive."""
        mock_sub = MagicMock(spec=EntitySubscription)
        mock_sub.is_active = False
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.unsubscribe_entity_by_token(token=str(uuid.uuid4()))
            assert not result.ok

    def test_success(self, mutations):
        """Test successful unsubscribe by token."""
        mock_sub = MagicMock(spec=EntitySubscription)
        mock_sub.is_active = True
        with patch(
            "apps.owasp.api.internal.mutations.entity_subscription.EntitySubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.unsubscribe_entity_by_token(token=str(uuid.uuid4()))
            assert result.ok
            assert mock_sub.is_active is False
            mock_sub.save.assert_called_once()
