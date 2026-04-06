"""Tests for event signal handlers."""

from unittest.mock import MagicMock, patch

from apps.owasp.signals.event import event_post_save


class TestEventSignals:
    """Test event post_save signal handler."""

    @patch("apps.owasp.signals.event.publish_event_notification")
    def test_event_created_publishes_created_notification(self, mock_publish):
        """Test that creating an event publishes a 'created' notification."""
        event = MagicMock()
        event_post_save(sender=None, instance=event, created=True)
        mock_publish.assert_called_once_with(event, "created")

    @patch("apps.owasp.signals.event.publish_event_notification")
    def test_event_updated_publishes_updated_notification(self, mock_publish):
        """Test that updating an event publishes an 'updated' notification."""
        event = MagicMock()
        # Set up previous values that match current values - no changes, no notification
        event._previous_values = {
            "name": "Test Event",
            "start_date": "2026-01-01",
            "end_date": "2026-01-02",
            "suggested_location": "Test Location",
            "url": "https://test.com",
            "description": "Test description",
        }
        # Set current values to be the same - no notification should be sent
        event.name = "Test Event"
        event.start_date = "2026-01-01"
        event.end_date = "2026-01-02"
        event.suggested_location = "Test Location"
        event.url = "https://test.com"
        event.description = "Test description"
        event_post_save(sender=None, instance=event, created=False)
        # No changes, so no notification should be published
        mock_publish.assert_not_called()
