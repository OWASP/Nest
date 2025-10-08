"""Google Calendar Events Handlers."""

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone
from httplib2.error import ServerNotFoundError

from apps.common.constants import NL
from apps.slack.blocks import get_pagination_buttons, markdown

PERMISSIONS_BLOCK = [markdown("*You do not have the permission to access calendar events.*")]


def get_cancel_reminder_blocks(reminder_schedule_id: int, slack_user_id: str) -> list[dict]:
    """Get the blocks for canceling a reminder."""
    from apps.nest.auth.calendar_events import has_calendar_events_permission
    from apps.nest.models.reminder_schedule import ReminderSchedule
    from apps.nest.schedulers.calendar_events.slack import SlackScheduler

    if not has_calendar_events_permission(slack_user_id):
        return PERMISSIONS_BLOCK
    try:
        reminder_schedule = ReminderSchedule.objects.get(pk=reminder_schedule_id)
    except ReminderSchedule.DoesNotExist:
        return [markdown("*Please provide a valid reminder number.*")]
    if reminder_schedule.reminder.member.slack_user_id != slack_user_id:
        return [markdown("*You can only cancel your own reminders.*")]
    SlackScheduler(reminder_schedule).cancel()
    return [
        markdown(
            f"*Canceled the reminder for event '{reminder_schedule.reminder.event.name}'*"
            f" in {reminder_schedule.reminder.channel_id}"
        )
    ]


def get_events_blocks(slack_user_id: str, presentation, page: int = 1) -> list[dict]:
    """Get Google Calendar events blocks for Slack home view."""
    from apps.nest.auth.calendar_events import has_calendar_events_permission
    from apps.nest.clients.google_calendar import GoogleCalendarClient
    from apps.nest.models.google_account_authorization import GoogleAccountAuthorization
    from apps.owasp.models.event import Event

    if not has_calendar_events_permission(slack_user_id):
        return PERMISSIONS_BLOCK

    # Authorize with Google
    auth = GoogleAccountAuthorization.authorize(slack_user_id)
    # If not authorized, we will get a tuple with the authorization URL
    if not isinstance(auth, GoogleAccountAuthorization):
        return [markdown(f"*Please sign in with Google first through this <{auth[0]}|link>*")]
    try:
        # Get a 24-hour window of events
        client = GoogleCalendarClient(auth)
        min_time = timezone.now() + timezone.timedelta(days=(page - 1))
        max_time = min_time + timezone.timedelta(days=1)
        events = client.get_events(min_time=min_time, max_time=max_time)
    # Catch network errors
    except ServerNotFoundError:
        return [markdown("*Please check your internet connection.*")]
    parsed_events = Event.parse_google_calendar_events(events)
    if not (events or parsed_events):
        return [markdown("*No upcoming calendar events found.*")]
    blocks = [
        markdown(
            f"*Your upcoming calendar events from {min_time.strftime('%Y-%m-%d %H:%M')}"
            f" to {max_time.strftime('%Y-%m-%d %H:%M %Z')}*"
            f"{NL}You can set a reminder for an event with `/nestbot reminder set "
            "--channel [channel] --event_number [event number] --minutes_before [minutes before]"
            " --message [optional message] --recurrence [recurrence]`"
        )
    ]
    for i, event in enumerate(parsed_events):
        # We will need this number later to set reminders
        # We are multiplying by 1000 to avoid collisions between pages
        # as we don't get the length of events list from Google Calendar API.
        event_number = (i + 1) + 1000 * (page - 1)
        # We will show the user the event number and cache the event ID for later use.
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


def get_reminders_blocks(slack_user_id: str) -> list[dict]:
    """Get reminders blocks for Slack home view."""
    from apps.nest.auth.calendar_events import has_calendar_events_permission
    from apps.nest.models.reminder_schedule import ReminderSchedule

    if not has_calendar_events_permission(slack_user_id):
        return PERMISSIONS_BLOCK

    reminders_schedules = ReminderSchedule.objects.filter(
        reminder__member__slack_user_id=slack_user_id,
    ).order_by("scheduled_time")
    if not reminders_schedules:
        return [markdown("*No reminders found. You can set one with `/nestbot reminder set`*")]
    blocks = [markdown("*Your upcoming reminders:*")]
    blocks.extend(
        markdown(
            f"{NL}- Reminder Number: {reminder_schedule.pk}"
            f"{NL}- Channel: {reminder_schedule.reminder.channel_id}"
            f"{NL}- Scheduled Time: "
            f"{reminder_schedule.scheduled_time.strftime('%Y-%m-%d, %H:%M %Z')}"
            f"{NL}- Recurrence: {reminder_schedule.recurrence}"
            f"{NL}- Message: {reminder_schedule.reminder.message or 'No message'}"
        )
        for reminder_schedule in reminders_schedules
    )
    return blocks


def get_setting_reminder_blocks(args, slack_user_id: str) -> list[dict]:
    """Get the blocks for setting a reminder."""
    from apps.nest.auth.calendar_events import has_calendar_events_permission
    from apps.nest.handlers.calendar_events import set_reminder
    from apps.nest.schedulers.calendar_events.slack import SlackScheduler

    if not has_calendar_events_permission(slack_user_id):
        return PERMISSIONS_BLOCK

    try:
        reminder_schedule = set_reminder(
            channel=args.channel,
            event_number=args.event_number,
            user_id=slack_user_id,
            minutes_before=args.minutes_before,
            recurrence=args.recurrence,
            message=" ".join(args.message) if args.message else "",
        )
        SlackScheduler(reminder_schedule).schedule()
        SlackScheduler.send_message(
            f"<@{reminder_schedule.reminder.member.slack_user_id}> set a reminder: "
            f"{reminder_schedule.reminder.message}"
            f" at {reminder_schedule.scheduled_time.strftime('%Y-%m-%d %H:%M %Z')}",
            reminder_schedule.reminder.channel_id,
        )
    except ValidationError as e:
        return [markdown(f"*{e.message}*")]
    except ValueError as e:
        return [markdown(f"*{e!s}*")]
    except ServerNotFoundError:
        return [markdown("*Please check your internet connection.*")]
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
