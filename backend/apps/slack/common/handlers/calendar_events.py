"""Google Calendar Events Handlers."""

from django.utils import timezone

from apps.common.constants import NL
from apps.slack.blocks import get_pagination_buttons, markdown


def get_blocks(slack_user_id: str, presentation, page: int = 1) -> list[dict]:
    """Get Google Calendar events blocks for Slack home view."""
    from apps.nest.clients.google_calendar import GoogleCalendarClient
    from apps.nest.models.google_account_authorization import GoogleAccountAuthorization
    from apps.owasp.models.event import Event

    auth = GoogleAccountAuthorization.authorize(slack_user_id)
    if not isinstance(auth, GoogleAccountAuthorization):
        return [markdown("*Please sign in to Google first.*")]
    client = GoogleCalendarClient(auth)
    min_time = timezone.now() + timezone.timedelta(days=(page - 1))
    max_time = min_time + timezone.timedelta(days=1)
    events = client.get_events(min_time=min_time, max_time=max_time)
    if not events:
        return [markdown("*No upcoming calendar events found.*")]
    parsed_events = Event.parse_google_calendar_events(events)
    blocks = [
        markdown(
            f"*Your upcoming calendar events from {min_time.strftime('%Y-%m-%d %H:%M')}"
            f" to {max_time.strftime('%Y-%m-%d %H:%M')}*"
        )
    ]
    for event in parsed_events:
        blocks.extend(
            [
                markdown(
                    f"*Name: {event.name}*"
                    f"{NL}*ID: {event.google_calendar_id}*"
                    f"{NL}- Starts at: {event.start_date.strftime('%Y-%m-%d %H:%M')} GMT"
                    f"{NL}- Ends at: {event.end_date.strftime('%Y-%m-%d %H:%M')} GMT"
                )
            ]
        )
    if presentation.include_pagination and (
        pagination_block := get_pagination_buttons("calendar_events", page, page + 1)
    ):
        blocks.append(
            {
                "type": "actions",
                "elements": pagination_block,
            }
        )
    return blocks
