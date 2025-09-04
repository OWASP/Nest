"""Google Calendar API Client."""

from django.utils import timezone
from googleapiclient.discovery import build

from apps.nest.models.google_account_authorization import GoogleAccountAuthorization


class GoogleCalendarClient:
    """Google Calendar API Client Class."""

    def __init__(self, google_account_authorization: GoogleAccountAuthorization):
        """Initialize the Google Calendar API Client."""
        self.google_account_authorization = google_account_authorization
        self.service = build(
            "calendar", "v3", credentials=google_account_authorization.credentials
        )

    def get_events(self):
        """Retrieve events from Google Calendar."""
        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=timezone.now().isoformat(),
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])
