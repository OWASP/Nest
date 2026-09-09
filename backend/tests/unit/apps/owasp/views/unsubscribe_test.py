"""Tests for one-click unsubscribe view."""

import uuid
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import RequestFactory

from apps.owasp.models.snapshot_subscription import SnapshotSubscription
from apps.owasp.views.unsubscribe import OneClickUnsubscribeView


class TestOneClickUnsubscribeView:
    """Test OneClickUnsubscribeView."""

    def setup_method(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.view = OneClickUnsubscribeView()
        self.token = uuid.uuid4()

    @patch("apps.owasp.views.unsubscribe.OneClickUnsubscribeView.find_subscription")
    def test_post_success(self, mock_find):
        """Test POST unsubscribe deletes subscription."""
        mock_sub = MagicMock()
        mock_find.return_value = mock_sub

        request = self.factory.post(f"/unsubscribe/{self.token}/")
        response = self.view.post(request, token=self.token)

        assert response.status_code == 200
        mock_sub.delete.assert_called_once()

    @patch("apps.owasp.views.unsubscribe.OneClickUnsubscribeView.find_subscription")
    def test_get_returns_confirmation_page(self, mock_find):
        """Test GET returns confirmation page without deleting subscription."""
        mock_sub = MagicMock()
        mock_find.return_value = mock_sub

        request = self.factory.get(f"/unsubscribe/{self.token}/")
        response = self.view.get(request, token=self.token)

        assert response.status_code == 200
        assert b"Confirm Unsubscribe" in response.content
        mock_sub.delete.assert_not_called()

    @patch("apps.owasp.views.unsubscribe.OneClickUnsubscribeView.find_subscription")
    def test_not_found(self, mock_find):
        """Test returns 404 when no subscription matches token."""
        mock_find.return_value = None

        request = self.factory.post(f"/unsubscribe/{self.token}/")
        response = self.view.post(request, token=self.token)

        assert response.status_code == 404

    @patch("apps.owasp.views.unsubscribe.OneClickUnsubscribeView.find_subscription")
    def test_response_body(self, mock_find):
        """Test successful unsubscribe returns JSON message."""
        mock_sub = MagicMock()
        mock_find.return_value = mock_sub

        request = self.factory.post(f"/unsubscribe/{self.token}/")
        response = self.view.post(request, token=self.token)

        assert response.status_code == 200
        assert b"Successfully unsubscribed" in response.content


class TestFindSubscription:
    """Test OneClickUnsubscribeView.find_subscription."""

    @patch("apps.owasp.views.unsubscribe.SnapshotSubscription")
    def test_finds_snapshot_subscription(self, mock_snapshot_model):
        """Test finds snapshot subscription by token."""
        token = uuid.uuid4()
        mock_sub = MagicMock()
        mock_snapshot_model.objects.get.return_value = mock_sub

        result = OneClickUnsubscribeView.find_subscription(token)

        assert result == mock_sub
        mock_snapshot_model.objects.get.assert_called_once_with(unsubscribe_token=token)

    @patch("apps.owasp.views.unsubscribe.SnapshotSubscription")
    def test_returns_none_when_not_found(self, mock_snapshot_model):
        """Test returns None when no subscription matches token."""
        token = uuid.uuid4()
        mock_snapshot_model.DoesNotExist = SnapshotSubscription.DoesNotExist
        mock_snapshot_model.objects.get.side_effect = SnapshotSubscription.DoesNotExist

        result = OneClickUnsubscribeView.find_subscription(token)

        assert result is None

    @patch("apps.owasp.views.unsubscribe.SnapshotSubscription")
    def test_returns_none_on_validation_error(self, mock_snapshot_model):
        """Test returns None when token causes ValidationError."""
        invalid_uuid = "not-a-valid-uuid"
        mock_snapshot_model.DoesNotExist = Exception
        mock_snapshot_model.objects.get.side_effect = ValidationError("Invalid UUID")

        result = OneClickUnsubscribeView.find_subscription(invalid_uuid)

        assert result is None
