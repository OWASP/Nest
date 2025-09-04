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

    def get_events(self, min_time=None, max_time=None) -> list[dict]:
        """Retrieve events from Google Calendar."""
        if not min_time:
            min_time = timezone.now()
        if not max_time:
            max_time = min_time + timezone.timedelta(days=1)
        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=min_time.isoformat(),
                timeMax=max_time.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])
