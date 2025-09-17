"""Nest Calendar Events utilities."""

import shlex
from argparse import ArgumentParser
from datetime import timedelta

from django.utils import timezone

from apps.nest.models.reminder_schedule import ReminderSchedule


def parse_reminder_args(text: str):
    """Parse reminder command arguments.

    Args:
        text (str): The text containing the reminder command arguments.

    Returns:
        Namespace: The parsed arguments as a Namespace object.

    """
    parser = ArgumentParser(prog="/set-reminder", description="Set a reminder for a Slack event.")
    parser.add_argument(
        "--channel", type=str, help="The channel to send the reminder to.", required=True
    )
    parser.add_argument(
        "--event_number", type=int, help="The event number to set the reminder for.", required=True
    )
    parser.add_argument(
        "--minutes_before",
        type=int,
        help="Minutes before the event to send the reminder.",
        default=10,
    )
    parser.add_argument(
        "--message",
        type=str,
        nargs="*",
        default=[],
        help="Optional message to include in the reminder.",
    )
    parser.add_argument(
        "--recurrence",
        type=str,
        choices=["once", "daily", "weekly", "monthly"],
        default="once",
        help="Optional recurrence pattern for the reminder.",
    )

    return parser.parse_args(shlex.split(text or ""))


def parse_cancel_reminder_args(text: str):
    """Parse cancel reminder command arguments.

    Args:
        text (str): The text containing the cancel reminder command arguments.

    Returns:
        Namespace: The parsed arguments as a Namespace object.

    """
    parser = ArgumentParser(prog="/cancel-reminder", description="Cancel a scheduled reminder.")
    parser.add_argument(
        "--number",
        type=int,
        help="The reminder number to cancel.",
        required=True,
    )

    return parser.parse_args(shlex.split(text or ""))


def update_reminder_schedule_date(reminder_schedule: ReminderSchedule) -> None:
    """Update the scheduled_time of a ReminderSchedule based on its recurrence pattern.

    Args:
        reminder_schedule (ReminderSchedule): The ReminderSchedule instance to update.

    Returns:
        None: The function updates the instance in place and saves it.

    """
    if reminder_schedule.scheduled_time > timezone.now():
        return  # No update needed if the scheduled time is in the future

    match reminder_schedule.recurrence:
        case ReminderSchedule.Recurrence.DAILY:
            reminder_schedule.scheduled_time += timedelta(days=1)
        case ReminderSchedule.Recurrence.WEEKLY:
            reminder_schedule.scheduled_time += timedelta(weeks=1)
        case ReminderSchedule.Recurrence.MONTHLY:
            reminder_schedule.scheduled_time.replace(
                month=reminder_schedule.scheduled_time.month + 1
            )
        case _:
            return  # No update for 'once' or unrecognized recurrence

    reminder_schedule.save(update_fields=["scheduled_time"])
