"""Handlers for Calendar Events."""

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.nest.clients.google_calendar import GoogleCalendarClient
from apps.nest.models.reminder import Reminder
from apps.nest.models.reminder_schedule import ReminderSchedule
from apps.owasp.models.entity_channel import EntityChannel
from apps.owasp.models.event import Event


def get_calendar_id(user_id: str, event_number: str) -> str:
    """Get the Google Calendar ID for a user."""
    if google_calendar_id := cache.get(f"{user_id}_{event_number}"):
        return google_calendar_id
    message = (
        "Invalid or expired event number. Please get a new event number from the events list."
    )
    raise ValidationError(message)


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
    channel: EntityChannel,
    minutes_before: int,
    client: GoogleCalendarClient,
    member,
    recurrence: str | None = None,
    google_calendar_id: str = "",
    message: str = "",
) -> ReminderSchedule:
    """Set a reminder for a user."""
    if minutes_before <= 0:
        message = "Minutes before must be a positive integer."
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

    with transaction.atomic():
        # Saving event to the database after validation
        event.save()

        reminder, _ = Reminder.objects.get_or_create(
            entity_channel=channel,
            event=event,
            member=member,
            defaults={"message": f"{event.name} - {message}" if message else event.name},
        )
        return schedule_reminder(
            reminder=reminder,
            scheduled_time=reminder_time,
            recurrence=recurrence or ReminderSchedule.Recurrence.ONCE,
        )
