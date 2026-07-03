"""Tests for snapshot subscription GraphQL mutations."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.owasp.api.internal.mutations.snapshot_subscription import (
    CreateSnapshotSubscriptionInput,
    SnapshotSubscriptionMutations,
    SnapshotSubscriptionResult,
    UpdateSnapshotSubscriptionInput,
)
from apps.owasp.models.snapshot_subscription import SnapshotSubscription

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


class TestSnapshotSubscriptionResult:
    """Test cases for SnapshotSubscriptionResult."""

    def test_result_ok(self):
        result = SnapshotSubscriptionResult(ok=True, message="Success")
        assert result.ok
        assert result.message == "Success"

    def test_result_not_ok(self):
        result = SnapshotSubscriptionResult(ok=False, message="Failed")
        assert not result.ok
        assert result.message == "Failed"


class TestCreateSnapshotSubscription:
    """Test cases for createSnapshotSubscription mutation."""

    @pytest.fixture
    def mutations(self):
        return SnapshotSubscriptionMutations()

    def test_duplicate_active_subscription(self, mutations):
        """Test create fails when active subscription already exists."""
        info = mock_info()
        input_data = CreateSnapshotSubscriptionInput()
        mock_existing = MagicMock(spec=SnapshotSubscription)
        mock_existing.is_active = True
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get_or_create.return_value = (mock_existing, False)
            result = mutations.create_snapshot_subscription(info, input_data=input_data)
            assert not result.ok
            assert result.message == "Subscription already exists."

    def test_reactivate_inactive_subscription(self, mutations):
        """Test create reactivates an inactive subscription."""
        info = mock_info()
        input_data = CreateSnapshotSubscriptionInput(frequency="weekly")
        mock_existing = MagicMock(spec=SnapshotSubscription)
        mock_existing.is_active = False
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get_or_create.return_value = (mock_existing, False)
            result = mutations.create_snapshot_subscription(info, input_data=input_data)
            assert result.ok
            assert result.message == "Subscription reactivated successfully."
            assert mock_existing.is_active is True
            mock_existing.save.assert_called_once()

    def test_reactivate_inactive_subscription_with_m2m_fields(self, mutations):
        """Test create reactivates an inactive subscription with M2M fields."""
        info = mock_info()
        input_data = CreateSnapshotSubscriptionInput(
            frequency="weekly",
            subscribed_chapter_ids=[3, 4],
        )
        mock_existing = MagicMock(spec=SnapshotSubscription)
        mock_existing.is_active = False
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get_or_create.return_value = (mock_existing, False)
            result = mutations.create_snapshot_subscription(info, input_data=input_data)
            assert result.ok
            assert result.message == "Subscription reactivated successfully."
            assert mock_existing.is_active is True
            mock_existing.save.assert_called_once()
            mock_existing.chapters.set.assert_called_once_with([3, 4])

    def test_invalid_frequency(self, mutations):
        """Test create fails with invalid frequency."""
        info = mock_info()
        input_data = CreateSnapshotSubscriptionInput(frequency="daily")
        result = mutations.create_snapshot_subscription(info, input_data=input_data)
        assert not result.ok
        assert "Invalid frequency" in result.message

    def test_success(self, mutations):
        """Test successful subscription creation."""
        info = mock_info()
        input_data = CreateSnapshotSubscriptionInput(frequency="weekly")
        mock_sub = MagicMock(spec=SnapshotSubscription)
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get_or_create.return_value = (mock_sub, True)
            result = mutations.create_snapshot_subscription(info, input_data=input_data)
            assert result.ok
            assert result.message == "Subscription created successfully."
            assert result.subscription == mock_sub

    def test_success_with_m2m_fields(self, mutations):
        """Test successful creation with subscribed chapters."""
        info = mock_info()
        input_data = CreateSnapshotSubscriptionInput(
            frequency="weekly",
            subscribed_chapter_ids=[4, 5],
        )
        mock_sub = MagicMock(spec=SnapshotSubscription)
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get_or_create.return_value = (mock_sub, True)
            result = mutations.create_snapshot_subscription(info, input_data=input_data)
            assert result.ok
            mock_sub.chapters.set.assert_called_once_with([4, 5])

    def test_concurrent_create_integrity_error(self, mutations):
        """Test create handles race condition with IntegrityError."""
        info = mock_info()
        input_data = CreateSnapshotSubscriptionInput(frequency="weekly")
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get_or_create.side_effect = IntegrityError
            result = mutations.create_snapshot_subscription(info, input_data=input_data)
            assert not result.ok
            assert result.message == "Subscription already exists."

    def test_create_after_cancel(self, mutations):
        """Test user can create subscription after cancelling previous one."""
        info = mock_info()
        input_data = CreateSnapshotSubscriptionInput(frequency="monthly")
        mock_existing = MagicMock(spec=SnapshotSubscription)
        mock_existing.is_active = False
        mock_existing.frequency = "weekly"
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get_or_create.return_value = (mock_existing, False)
            result = mutations.create_snapshot_subscription(info, input_data=input_data)
            assert result.ok
            assert result.message == "Subscription reactivated successfully."
            assert mock_existing.is_active is True
            assert mock_existing.frequency == "monthly"
            mock_existing.save.assert_called_once()


class TestUpdateSnapshotSubscription:
    """Test cases for updateSnapshotSubscription mutation."""

    @pytest.fixture
    def mutations(self):
        return SnapshotSubscriptionMutations()

    def test_not_found(self, mutations):
        """Test update fails when subscription doesn't exist."""
        info = mock_info()
        input_data = UpdateSnapshotSubscriptionInput()
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.side_effect = SnapshotSubscription.DoesNotExist
            result = mutations.update_snapshot_subscription(info, input_data=input_data)
            assert not result.ok
            assert result.message == "Subscription not found."

    def test_invalid_frequency(self, mutations):
        """Test update fails with invalid frequency."""
        info = mock_info()
        input_data = UpdateSnapshotSubscriptionInput(frequency="daily")
        mock_sub = MagicMock(spec=SnapshotSubscription)
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.update_snapshot_subscription(info, input_data=input_data)
            assert not result.ok
            assert "Invalid frequency" in result.message

    def test_success(self, mutations):
        """Test successful subscription update."""
        info = mock_info()
        input_data = UpdateSnapshotSubscriptionInput(frequency="monthly", include_chapters=False)
        mock_sub = MagicMock(spec=SnapshotSubscription)
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.update_snapshot_subscription(info, input_data=input_data)
            assert result.ok
            assert result.message == "Subscription updated successfully."
            mock_sub.save.assert_called_once()

    def test_success_with_m2m_fields(self, mutations):
        """Test successful update with subscribed chapters."""
        info = mock_info()
        input_data = UpdateSnapshotSubscriptionInput(
            subscribed_chapter_ids=[30],
        )
        mock_sub = MagicMock(spec=SnapshotSubscription)
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.update_snapshot_subscription(info, input_data=input_data)
            assert result.ok
            mock_sub.chapters.set.assert_called_once_with([30])


class TestCancelSnapshotSubscription:
    """Test cases for cancelSnapshotSubscription mutation."""

    @pytest.fixture
    def mutations(self):
        return SnapshotSubscriptionMutations()

    def test_not_found(self, mutations):
        """Test cancel fails when subscription doesn't exist."""
        info = mock_info()
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.side_effect = SnapshotSubscription.DoesNotExist
            result = mutations.cancel_snapshot_subscription(info)
            assert not result.ok
            assert result.message == "Subscription not found."

    def test_success(self, mutations):
        """Test successful subscription cancellation."""
        info = mock_info()
        mock_sub = MagicMock(spec=SnapshotSubscription)
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.cancel_snapshot_subscription(info)
            assert result.ok
            assert result.message == "Subscription cancelled successfully."
            assert mock_sub.is_active is False
            mock_sub.save.assert_called_once()


class TestUnsubscribeByToken:
    """Test cases for unsubscribeByToken mutation."""

    @pytest.fixture
    def mutations(self):
        return SnapshotSubscriptionMutations()

    def test_invalid_token(self, mutations):
        """Test unsubscribe fails with invalid token."""
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.side_effect = SnapshotSubscription.DoesNotExist
            result = mutations.unsubscribe_by_token(token=str(uuid.uuid4()))
            assert not result.ok
            assert result.message == "Invalid unsubscribe token."

    def test_malformed_token(self, mutations):
        """Test unsubscribe fails with malformed token."""
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.side_effect = ValidationError("Invalid UUID")
            result = mutations.unsubscribe_by_token(token=MOCK_TOKEN)
            assert not result.ok
            assert result.message == "Invalid unsubscribe token."

    def test_already_inactive(self, mutations):
        """Test unsubscribe fails when already inactive."""
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_sub.is_active = False
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.unsubscribe_by_token(token=str(uuid.uuid4()))
            assert not result.ok
            assert result.message == "Subscription is already inactive."

    def test_success(self, mutations):
        """Test successful unsubscribe by token."""
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_sub.is_active = True
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.unsubscribe_by_token(token=str(uuid.uuid4()))
            assert result.ok
            assert result.message == "Successfully unsubscribed."
            assert mock_sub.is_active is False
            mock_sub.save.assert_called_once()
