"""Handlers for Calendar Events."""

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
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
) -> ReminderSchedule:
    """Schedule a reminder."""
    if scheduled_time < timezone.now():
        message = "Scheduled time must be in the future."
        raise ValidationError(message)
    if recurrence not in ReminderSchedule.Recurrence.values:
        message = "Invalid recurrence value."
        raise ValidationError(message)
    return ReminderSchedule.objects.create(
        reminder=reminder,
        scheduled_time=scheduled_time,
        recurrence=recurrence,
    )


def set_reminder(
    channel: str,
    event_number: str,
    user_id: str,
    minutes_before: int,
    recurrence: str | None = None,
    message: str = "",
) -> ReminderSchedule:
    """Set a reminder for a user."""
    if minutes_before <= 0:
        message = "Minutes before must be a positive integer."
        raise ValidationError(message)
    auth = GoogleAccountAuthorization.authorize(user_id)
    if not isinstance(auth, GoogleAccountAuthorization):
        message = "User is not authorized with Google. Please sign in first."
        raise ValidationError(message)
    google_calendar_id = cache.get(f"{user_id}_{event_number}")
    if not google_calendar_id:
        message = (
            "Invalid or expired event number. Please get a new event number from the events list."
        )
        raise ValidationError(message)

    client = GoogleCalendarClient(auth)
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

    with transaction.atomic():
        # Saving event to the database after validation
        event.save()

        member = Member.objects.get(slack_user_id=user_id)
        reminder, _ = Reminder.objects.get_or_create(
            channel_id=channel,
            event=event,
            member=member,
            defaults={"message": f"{event.name} - {message}" if message else event.name},
        )
        return schedule_reminder(
            reminder=reminder,
            scheduled_time=reminder_time,
            recurrence=recurrence or ReminderSchedule.Recurrence.ONCE,
        )
