"""Test cases for Google Calendar API client."""

from unittest.mock import patch

from django.test import override_settings
from django.utils import timezone

from apps.nest.clients.google_calendar import GoogleCalendarClient
from apps.nest.models.google_account_authorization import GoogleAccountAuthorization

EVENT_NAME = "Test Event"
EVENT_START = "2025-05-26T09:00:00-07:00"


class TestGoogleCalendarClient:
    """Test cases for Google Calendar API client."""

    @override_settings(IS_GOOGLE_AUTH_ENABLED=True, IS_AWS_KMS_ENABLED=True)
    @patch("apps.nest.clients.google_calendar.build")
    def test_init(self, mock_build):
        """Test the initialization of GoogleCalendarClient."""
        auth = GoogleAccountAuthorization(
            access_token="mock_access_token",  # noqa: S106
            refresh_token="mock_refresh_token",  # noqa: S106
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        client = GoogleCalendarClient(google_account_authorization=auth)
        assert client.google_account_authorization == auth
        mock_build.assert_called_once()

    @override_settings(IS_GOOGLE_AUTH_ENABLED=True, IS_AWS_KMS_ENABLED=True)
    @patch.object(GoogleCalendarClient, "get_events")
    def test_get_events(self, mock_get_events):
        """Test the retrieval of events from Google Calendar."""
        mock_get_events.return_value = [
            {
                "id": "12345",
                "summary": EVENT_NAME,
                "start": {"dateTime": EVENT_START},
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
        assert events[0]["summary"] == EVENT_NAME

    @override_settings(IS_GOOGLE_AUTH_ENABLED=True, IS_AWS_KMS_ENABLED=True)
    @patch.object(GoogleCalendarClient, "get_event")
    def test_get_event(self, mock_get_event):
        """Test the retrieval of a single event from Google Calendar."""
        mock_get_event.return_value = {
            "id": "12345",
            "summary": EVENT_NAME,
            "start": {"dateTime": EVENT_START},
            "end": {"dateTime": "2025-05-30T17:00:00-07:00"},
        }

        client = GoogleCalendarClient(
            google_account_authorization=GoogleAccountAuthorization(
                access_token="mock_access_token",  # noqa: S106
                refresh_token="mock_refresh_token",  # noqa: S106
                expires_at=timezone.now() + timezone.timedelta(hours=1),
            )
        )
        event = client.get_event(google_calendar_id="12345")
        assert event["id"] == "12345"
        assert event["summary"] == EVENT_NAME
        assert event["start"]["dateTime"] == EVENT_START
        assert event["end"]["dateTime"] == "2025-05-30T17:00:00-07:00"
        mock_get_event.assert_called_once_with(google_calendar_id="12345")
