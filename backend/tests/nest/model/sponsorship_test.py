from unittest.mock import Mock, patch

import pytest
from django.utils import timezone

from apps.github.models.issue import Issue
from apps.nest.models.sponsorship import Sponsorship

PRICE_USD = 100.0


class TestSponsorshipModel:
    @pytest.mark.parametrize(
        ("price_usd", "deadline_at", "slack_user_id"),
        [
            (100.0, timezone.now(), "U12345"),
            (200.0, None, "U67890"),
        ],
    )
    @patch.object(Sponsorship, "save")
    def test_update_data(self, mock_save, price_usd, deadline_at, slack_user_id):
        """Test the update_data method of the Sponsorship model."""
        sponsorship = Sponsorship()

        updated_sponsorship = Sponsorship.update_data(
            sponsorship,
            price_usd=price_usd,
            deadline_at=deadline_at,
            slack_user_id=slack_user_id,
        )

        assert updated_sponsorship.price_usd == price_usd
        assert updated_sponsorship.deadline_at == deadline_at
        assert updated_sponsorship.slack_user_id == slack_user_id
        mock_save.assert_called_once()

    @patch.object(Sponsorship, "save")
    def test_update_data_save_called(self, mock_save):
        """Test that the save method is called when updating sponsorship data."""
        sponsorship = Sponsorship()

        Sponsorship.update_data(
            sponsorship,
            price_usd=PRICE_USD,
            deadline_at=timezone.now(),
            slack_user_id="U12345",
        )

        mock_save.assert_called_once()

    @pytest.mark.parametrize(
        ("initial_price", "updated_price", "initial_deadline", "updated_deadline"),
        [
            (50.0, 100.0, timezone.now(), timezone.now()),
            (200.0, 150.0, None, timezone.now()),
        ],
    )
    @patch.object(Sponsorship, "save")
    def test_update_data_partial_updates(
        self, mock_save, initial_price, updated_price, initial_deadline, updated_deadline
    ):
        """Test partial updates using the update_data method."""
        sponsorship = Sponsorship(price_usd=initial_price, deadline_at=initial_deadline)

        Sponsorship.update_data(sponsorship, price_usd=updated_price)
        assert sponsorship.price_usd == updated_price
        assert sponsorship.deadline_at == initial_deadline
        mock_save.assert_called_once()

        mock_save.reset_mock()

        # Update only the deadline
        Sponsorship.update_data(sponsorship, deadline_at=updated_deadline)
        assert sponsorship.price_usd == updated_price
        assert sponsorship.deadline_at == updated_deadline
        mock_save.assert_called_once()

    @patch("apps.nest.models.sponsorship.Sponsorship.objects.create")
    def test_sponsorship_creation(self, mock_create):
        """Test creating a Sponsorship instance in the database."""
        issue = Mock(spec=Issue, title="Test Issue", url="https://github.com/OWASP/Nest/issues/1")
        issue._state = Mock()

        mock_create.return_value = Sponsorship(
            issue=issue,
            price_usd=PRICE_USD,
            slack_user_id="U12345",
        )

        sponsorship = Sponsorship.objects.create(
            issue=issue,
            price_usd=100.0,
            slack_user_id="U12345",
        )

        assert sponsorship.issue == issue
        assert sponsorship.price_usd == PRICE_USD
        assert sponsorship.slack_user_id == "U12345"
        assert sponsorship.deadline_at is None
        mock_create.assert_called_once_with(
            issue=issue,
            price_usd=100.0,
            slack_user_id="U12345",
        )

    @patch("apps.nest.models.sponsorship.Sponsorship.objects.create")
    def test_sponsorship_with_deadline(self, mock_create):
        """Test creating a Sponsorship instance with a deadline."""
        # Mock the Issue instance with _state attribute
        issue = Mock(spec=Issue, title="Test Issue", url="https://github.com/OWASP/Nest/issues/1")
        issue._state = Mock()

        deadline = timezone.now()

        # Mock the return value of Sponsorship.objects.create
        mock_create.return_value = Sponsorship(
            issue=issue,
            price_usd=100.0,
            slack_user_id="U12345",
            deadline_at=deadline,
        )

        sponsorship = Sponsorship.objects.create(
            issue=issue,
            price_usd=100.0,
            slack_user_id="U12345",
            deadline_at=deadline,
        )

        assert sponsorship.deadline_at == deadline
        mock_create.assert_called_once_with(
            issue=issue,
            price_usd=100.0,
            slack_user_id="U12345",
            deadline_at=deadline,
        )
