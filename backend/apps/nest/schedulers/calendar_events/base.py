"""Base Scheduler for Nest Calendar Events."""

from django_rq import get_scheduler

from apps.nest.models.reminder_schedule import ReminderSchedule


class BaseScheduler:
    """Base Scheduler Class for Nest Calendar Events."""

    def __init__(self, reminder_schedule: ReminderSchedule):
        """Initialize the BaseScheduler with a ReminderSchedule instance."""
        self.reminder_schedule = reminder_schedule
        self.scheduler = get_scheduler("default")
