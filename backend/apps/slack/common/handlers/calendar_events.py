"""Google Calendar Events Handlers."""

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone
from googleapiclient.errors import Error
from httplib2.error import ServerNotFoundError

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
                f"{NL}- Starts at: {event.start_date.strftime('%Y-%m-%d %H:%M %Z')}"
                f"{NL}- Ends at: {event.end_date.strftime('%Y-%m-%d %H:%M %Z')}"
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
    from apps.nest.controllers.calendar_events import set_reminder

    try:
        reminder_schedule = set_reminder(
            channel=args.channel,
            event_number=args.event_number,
            slack_user_id=slack_user_id,
            minutes_before=args.minutes_before,
            recurrence=args.recurrence,
            message=" ".join(args.message) if args.message else "",
        )
    except ValidationError as e:
        return [markdown(f"*{e.message}*")]
    except (ServerNotFoundError, Error):
        return [markdown("*An unexpected error occurred. Please try again later.*")]
    return [
        markdown(
            f"*{args.minutes_before}-minute reminder set for event"
            f" '{reminder_schedule.reminder.event.name}'*"
            f" in {args.channel}"
            f"{NL} Scheduled Time: "
            f"{reminder_schedule.scheduled_time.strftime('%Y-%m-%d %H:%M %Z')}"
            f"{NL} Recurrence: {reminder_schedule.recurrence}"
            f"{NL} Message: {reminder_schedule.reminder.message}"
        )
    ]
