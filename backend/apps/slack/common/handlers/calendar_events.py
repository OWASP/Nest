"""Google Calendar Events Handlers."""

from django.core.cache import cache
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
        return [markdown(f"*Please sign in with Google first through this <{auth[0]}|link>*")]
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
            f"{NL}Set a reminder for an event with `/set-reminder [channel]"
            " [event number] [minutes before] [optional message] [recurrence]`"
        )
    ]
    for i, event in enumerate(parsed_events):
        event_number = i + 1
        cache.set(f"{slack_user_id}_{event_number}", event.google_calendar_id, timeout=3600)
        blocks.append(
            markdown(
                f"*Name: {event.name}*"
                f"{NL}*Number: {event_number}*"
                f"{NL}- Starts at: {event.start_date.strftime('%Y-%m-%d %H:%M')} GMT"
                f"{NL}- Ends at: {event.end_date.strftime('%Y-%m-%d %H:%M')} GMT"
            )
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


def get_reminder_blocks(args, slack_user_id: str) -> list[dict]:
    """Get the blocks for setting a reminder."""
    from apps.nest.clients.google_calendar import GoogleCalendarClient
    from apps.nest.models.google_account_authorization import GoogleAccountAuthorization
    from apps.nest.models.reminder import Reminder
    from apps.owasp.models.event import Event

    auth = GoogleAccountAuthorization.authorize(slack_user_id)
    if not isinstance(auth, GoogleAccountAuthorization):
        return [markdown(f"*Please sign in with Google first through this <{auth[0]}|link>*")]
    client = GoogleCalendarClient(auth)
    google_calendar_id = cache.get(f"{slack_user_id}_{args.event_number}")
    if not google_calendar_id:
        return [
            markdown(
                "*Invalid or expired event number. Please check the event number and try again.*"
            )
        ]
    event = Event.parse_google_calendar_event(client.get_event(google_calendar_id))

    if not event:
        return [markdown("*Could not retrieve the event details. Please try again later.*")]
    reminder_time = event.start_date - timezone.timedelta(minutes=args.minutes_before)
    if reminder_time <= timezone.now():
        return [
            markdown(
                "*The reminder time must be in the future. Please adjust the minutes before.*"
            )
        ]
    Reminder.set_reminder(
        slack_user_id=slack_user_id,
        channel=args.channel,
        event=event,
        reminder_time=reminder_time,
        message=args.message,
        recurrence=args.recurrence,
    )

    return [
        markdown(
            f"*Reminder set for event '{event.name}'"
            f" at {reminder_time.strftime('%Y-%m-%d %H:%M')} GMT*"
        )
    ]
