"""Controllers for Calendar Events."""

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.nest.clients.google_calendar import GoogleCalendarClient
from apps.nest.models.google_account_authorization import GoogleAccountAuthorization
from apps.nest.models.reminder import Reminder
from apps.nest.models.reminder_schedule import ReminderSchedule
from apps.owasp.models.event import Event
from apps.slack.models.member import Member


def schedule_reminder(
    reminder: Reminder,
    scheduled_time: timezone.datetime,
    recurrence=ReminderSchedule.Recurrence.ONCE,
):
    """Schedule a reminder."""
    if scheduled_time < timezone.now():
        message = "Scheduled time must be in the future."
        raise ValidationError(message)
    if recurrence not in ReminderSchedule.Recurrence.values:
        message = "Invalid recurrence value."
        raise ValidationError(message)
    ReminderSchedule.objects.create(
        reminder=reminder,
        scheduled_time=scheduled_time,
        recurrence=recurrence,
    )


def set_reminder(
    channel: str,
    event_number: str,
    slack_user_id: str,
    minutes_before: int,
    recurrence: str | None = None,
    message: str = "",
) -> Reminder:
    """Set a reminder for a user."""
    auth = GoogleAccountAuthorization.authorize(slack_user_id)
    if not isinstance(auth, GoogleAccountAuthorization):
        message = "User is not authorized with Google. Please sign in first."
        raise ValidationError(message)
    client = GoogleCalendarClient(auth)
    google_calendar_id = cache.get(f"{slack_user_id}_{event_number}")
    if not google_calendar_id:
        message = (
            "Invalid or expired event number. Please get a new event number from the events list."
        )
        raise ValidationError(message)
    event = Event.parse_google_calendar_event(client.get_event(google_calendar_id))
    if not event:
        message = "Could not retrieve the event details. Please try again later."
        raise ValidationError(message)
    reminder_time = event.start_date - timezone.timedelta(minutes=minutes_before)
    if reminder_time < timezone.now():
        message = "Reminder time must be in the future. Please adjust the minutes before."
        raise ValidationError(message)
    if recurrence and recurrence not in ReminderSchedule.Recurrence.values:
        message = "Invalid recurrence value."
        raise ValidationError(message)
    member = Member.objects.get(slack_user_id=slack_user_id)
    reminder = Reminder.objects.create(
        channel_id=channel,
        event=event,
        member=member,
        message=f"{event.name} - {message}" if message else event.name,
    )
    schedule_reminder(
        reminder=reminder,
        scheduled_time=reminder_time,
        recurrence=recurrence or ReminderSchedule.Recurrence.ONCE,
    )
    return reminder
