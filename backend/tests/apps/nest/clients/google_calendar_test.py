"""Test cases for Google Calendar API client."""

from unittest.mock import patch

from django.test import override_settings
from django.utils import timezone

from apps.nest.clients.google_calendar import GoogleCalendarClient
from apps.nest.models.google_account_authorization import GoogleAccountAuthorization


class TestGoogleCalendarClient:
    """Test cases for Google Calendar API client."""

    @override_settings(IS_GOOGLE_AUTH_ENABLED=True, IS_AWS_KMS_ENABLED=True)
    @patch.object(GoogleCalendarClient, "get_events")
    def test_get_events(self, mock_get_events):
        """Test the retrieval of events from Google Calendar."""
        mock_get_events.return_value = [
            {
                "id": "12345",
                "summary": "Test Event",
                "start": {"dateTime": "2025-05-26T09:00:00-07:00"},
                "end": {"dateTime": "2025-05-30T17:00:00-07:00"},
            }
        ]

        client = GoogleCalendarClient(
            google_account_authorization=GoogleAccountAuthorization(
                access_token="mock_access_token",  # noqa: S106
                refresh_token="mock_refresh_token",  # noqa: S106
                expires_at=timezone.now() + timezone.timedelta(hours=1),
            )
        )
        events = client.get_events()
        assert len(events) == 1
        assert events[0]["id"] == "12345"
        assert events[0]["summary"] == "Test Event"
