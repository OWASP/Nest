"""Tests for snapshot subscription GraphQL mutations."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError

from apps.owasp.api.internal.mutations.snapshot_subscription import (
    CreateSnapshotSubscriptionInput,
    SnapshotSubscriptionMutations,
    SnapshotSubscriptionResult,
    UpdateSnapshotSubscriptionInput,
)
from apps.owasp.models.snapshot_subscription import MAX_SUBSCRIPTIONS, SnapshotSubscription

MOCK_TOKEN = "mock-unsubscribe-token"  # noqa: S105


def mock_info():
    """Create a mock GraphQL info object with authenticated user."""
    info = MagicMock()
    info.context.request.user = MagicMock(spec=True, pk=1)
    return info


class TestSnapshotSubscriptionResult:
    """Test SnapshotSubscriptionResult type."""

    def test_default_subscription_is_none(self):
        """Test default subscription field is None."""
        result = SnapshotSubscriptionResult(ok=True, message="test")
        assert result.subscription is None

    def test_result_with_subscription(self):
        """Test result includes subscription when provided."""
        mock_sub = MagicMock()
        result = SnapshotSubscriptionResult(ok=True, message="test", subscription=mock_sub)
        assert result.subscription == mock_sub

    def test_error_result(self):
        """Test error result without subscription."""
        result = SnapshotSubscriptionResult(ok=False, message="error")
        assert not result.ok
        assert result.message == "error"
        assert result.subscription is None


class TestCreateSnapshotSubscription:
    """Test cases for createSnapshotSubscription mutation."""

    @pytest.fixture
    def mutations(self):
        return SnapshotSubscriptionMutations()

    @pytest.fixture(autouse=True)
    def _mock_transaction(self):
        """Disable transaction.atomic for tests."""
        with (
            patch("django.db.transaction.Atomic.__enter__", return_value=None),
            patch("django.db.transaction.Atomic.__exit__", return_value=False),
        ):
            yield

    @patch("apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.create")
    def test_create_validation_error(self, mock_create, mutations):
        """Test create propagates ValidationError from clean()."""
        info = mock_info()
        input_data = CreateSnapshotSubscriptionInput(
            frequency="weekly",
            include_chapters=False,
            include_events=False,
            include_issues=False,
            include_posts=False,
            include_projects=False,
            include_pull_requests=False,
            include_releases=False,
            include_users=False,
        )
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_sub.clean.side_effect = ValidationError(
            "Your subscription cannot be empty. Please choose something to follow."
        )
        mock_create.return_value = mock_sub

        result = mutations.create_snapshot_subscription(info, input_data=input_data)
        assert not result.ok
        assert "subscription cannot be empty" in result.message

    @patch("apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.create")
    def test_create_success(self, mock_create, mutations):
        """Test successful subscription creation."""
        info = mock_info()
        input_data = CreateSnapshotSubscriptionInput(
            frequency="weekly", name="My Sub", include_chapters=True
        )
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_sub.has_duplicate_setup.return_value = False
        mock_create.return_value = mock_sub

        result = mutations.create_snapshot_subscription(info, input_data=input_data)

        assert result.ok
        assert result.message == "Subscription created successfully."
        assert result.subscription == mock_sub
        mock_sub.set_m2m_fields.assert_called_once()

    @patch("apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.create")
    def test_create_max_reached(self, mock_create, mutations):
        """Test create fails when max subscriptions reached."""
        info = mock_info()
        input_data = CreateSnapshotSubscriptionInput(frequency="weekly", include_chapters=True)
        mock_create.side_effect = ValidationError(
            f"Maximum number of subscriptions ({MAX_SUBSCRIPTIONS}) reached."
        )

        result = mutations.create_snapshot_subscription(info, input_data=input_data)

        assert not result.ok
        assert str(MAX_SUBSCRIPTIONS) in result.message

    @patch("apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.create")
    def test_create_duplicate_setup(self, mock_create, mutations):
        """Test create fails when duplicate setup exists."""
        info = mock_info()
        input_data = CreateSnapshotSubscriptionInput(
            frequency="weekly", name="Sub", include_chapters=True
        )
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_sub.has_duplicate_setup.return_value = True
        mock_create.return_value = mock_sub

        result = mutations.create_snapshot_subscription(info, input_data=input_data)

        assert not result.ok
        assert "same setup" in result.message


class TestUpdateSnapshotSubscription:
    """Test cases for updateSnapshotSubscription mutation."""

    @pytest.fixture(autouse=True)
    def _mock_transaction(self):
        """Disable transaction.atomic for tests."""
        with (
            patch("django.db.transaction.Atomic.__enter__", return_value=None),
            patch("django.db.transaction.Atomic.__exit__", return_value=False),
        ):
            yield

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
            result = mutations.update_snapshot_subscription(
                info, subscription_id=1, input_data=input_data
            )
            assert not result.ok
            assert result.message == "Subscription not found."

    def test_clean_validation_error(self, mutations):
        """Test update fails when clean() rejects the state."""
        info = mock_info()
        input_data = UpdateSnapshotSubscriptionInput(
            include_chapters=False,
        )
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_sub.clean.side_effect = ValidationError(
            "Your subscription cannot be empty. Please choose something to follow."
        )
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.update_snapshot_subscription(
                info, subscription_id=1, input_data=input_data
            )
            assert not result.ok
            assert "subscription cannot be empty" in result.message

    def test_success(self, mutations):
        """Test successful subscription update."""
        info = mock_info()
        input_data = UpdateSnapshotSubscriptionInput(
            frequency="monthly",
            name="Updated Name",
            include_chapters=False,
        )
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_sub.has_duplicate_setup.return_value = False
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.update_snapshot_subscription(
                info, subscription_id=1, input_data=input_data
            )
            assert result.ok
            assert result.message == "Subscription updated successfully."
            mock_sub.update.assert_called_once()
            mock_sub.set_m2m_fields.assert_called_once()
            mock_sub.clean.assert_called_once()

    def test_duplicate_setup_rejected(self, mutations):
        """Test update rolls back when duplicate setup detected."""
        info = mock_info()
        input_data = UpdateSnapshotSubscriptionInput(frequency="monthly")
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_sub.has_duplicate_setup.return_value = True
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.update_snapshot_subscription(
                info, subscription_id=1, input_data=input_data
            )
            assert not result.ok
            assert "same setup" in result.message


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
            result = mutations.cancel_snapshot_subscription(info, subscription_id=1)
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
            result = mutations.cancel_snapshot_subscription(info, subscription_id=1)
            assert result.ok
            mock_sub.deactivate.assert_called_once()


class TestDeleteSnapshotSubscription:
    """Test cases for deleteSnapshotSubscription mutation."""

    @pytest.fixture
    def mutations(self):
        return SnapshotSubscriptionMutations()

    def test_not_found(self, mutations):
        """Test delete fails when subscription doesn't exist."""
        info = mock_info()
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.side_effect = SnapshotSubscription.DoesNotExist
            result = mutations.delete_snapshot_subscription(info, subscription_id=1)
            assert not result.ok
            assert result.message == "Subscription not found."

    def test_success(self, mutations):
        """Test successful subscription deletion."""
        info = mock_info()
        mock_sub = MagicMock(spec=SnapshotSubscription)
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.delete_snapshot_subscription(info, subscription_id=1)
            assert result.ok
            mock_sub.delete.assert_called_once()


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
            result = mutations.unsubscribe_by_token(token="invalid")  # noqa: S106
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
            mock_sub.deactivate.assert_called_once()


class TestReactivateSnapshotSubscription:
    """Test cases for reactivateSnapshotSubscription mutation."""

    @pytest.fixture
    def mutations(self):
        return SnapshotSubscriptionMutations()

    def test_not_found(self, mutations):
        """Test reactivate fails when subscription doesn't exist."""
        info = mock_info()
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.side_effect = SnapshotSubscription.DoesNotExist
            result = mutations.reactivate_snapshot_subscription(info, subscription_id=1)
            assert not result.ok
            assert result.message == "Subscription not found."

    def test_already_active(self, mutations):
        """Test reactivate fails when already active."""
        info = mock_info()
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_sub.reactivate.side_effect = ValidationError("Subscription is already active.")
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.reactivate_snapshot_subscription(info, subscription_id=1)
            assert not result.ok
            assert result.message == "Subscription is already active."

    def test_max_active_reached(self, mutations):
        """Test reactivate fails when max active subscriptions reached."""
        info = mock_info()
        mock_sub = MagicMock(spec=SnapshotSubscription)
        mock_sub.reactivate.side_effect = ValidationError(
            f"Maximum number of active subscriptions ({MAX_SUBSCRIPTIONS}) reached."
        )
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.reactivate_snapshot_subscription(info, subscription_id=1)
            assert not result.ok
            assert str(MAX_SUBSCRIPTIONS) in result.message

    def test_success(self, mutations):
        """Test successful reactivation."""
        info = mock_info()
        mock_sub = MagicMock(spec=SnapshotSubscription)
        with patch(
            "apps.owasp.api.internal.mutations.snapshot_subscription.SnapshotSubscription.objects"
        ) as mock_objects:
            mock_objects.get.return_value = mock_sub
            result = mutations.reactivate_snapshot_subscription(info, subscription_id=1)
            assert result.ok
            mock_sub.reactivate.assert_called_once()
