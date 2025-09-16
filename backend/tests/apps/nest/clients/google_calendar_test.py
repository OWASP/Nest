"""Test cases for Google Calendar API client."""

from unittest.mock import MagicMock, patch

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
        auth = MagicMock(spec=GoogleAccountAuthorization)
        auth.credentials = "mock_credentials"
        client = GoogleCalendarClient(google_account_authorization=auth)
        assert client.google_account_authorization == auth
        mock_build.assert_called_once_with("calendar", "v3", credentials="mock_credentials")

    @override_settings(IS_GOOGLE_AUTH_ENABLED=True, IS_AWS_KMS_ENABLED=True)
    @patch("apps.nest.clients.google_calendar.build")
    def test_get_events(self, mock_build):
        """Test the retrieval of events from Google Calendar."""
        mock_build.return_value.events.return_value.list.return_value.execute.return_value = {
            "items": [
                {
                    "id": "12345",
                    "summary": EVENT_NAME,
                    "start": {"dateTime": EVENT_START},
                    "end": {"dateTime": "2025-05-30T17:00:00-07:00"},
                }
            ]
        }

        client = GoogleCalendarClient(
            google_account_authorization=GoogleAccountAuthorization(
                access_token="mock_access_token",  # noqa: S106
                refresh_token="mock_refresh_token",  # noqa: S106
                expires_at=timezone.now() + timezone.timedelta(hours=1),
            )
        )
        min_time = timezone.now()
        max_time = min_time + timezone.timedelta(days=5)
        events = client.get_events(min_time=min_time, max_time=max_time)
        assert len(events) == 1
        assert events[0]["id"] == "12345"
        assert events[0]["summary"] == EVENT_NAME
        mock_build.return_value.events.return_value.list.assert_called_once_with(
            calendarId="primary",
            timeMin=min_time.isoformat(),
            timeMax=max_time.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )

    @override_settings(IS_GOOGLE_AUTH_ENABLED=True, IS_AWS_KMS_ENABLED=True)
    @patch("apps.nest.clients.google_calendar.build")
    def test_get_event(self, mock_build):
        """Test the retrieval of a single event from Google Calendar."""
        mock_build.return_value.events.return_value.get.return_value.execute.return_value = {
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
        mock_build.return_value.events.return_value.get.assert_called_once_with(
            calendarId="primary", eventId="12345"
        )
