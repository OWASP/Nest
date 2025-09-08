"""Base Scheduler for Nest Calendar Events."""

from django_rq import get_queue, get_scheduler

from apps.nest.models.reminder_schedule import ReminderSchedule


class BaseScheduler:
    """Base Scheduler Class for Nest Calendar Events."""

    def __init__(self, reminder_schedule: ReminderSchedule):
        """Initialize the BaseScheduler with a ReminderSchedule instance."""
        self.reminder_schedule = reminder_schedule
        self.scheduler = get_scheduler("default")
        self.queue = get_queue("default")

    def schedule(self):
        """Schedule the reminder."""
        if self.reminder_schedule.recurrence == ReminderSchedule.Recurrence.ONCE:
            self.queue.enqueue_at(
                self.reminder_schedule.scheduled_time,
                self.send_message,
                args=(self.reminder_schedule.reminder.message,),
            )
            return

        self.scheduler.cron(
            self.reminder_schedule.cron_expression,
            func=self.send_message,
            args=(self.reminder_schedule.reminder.message,),
            queue_name="default",
        )

    def send_message(self, message: str):
        """Send the platform-specific message."""
        error_message = "Subclasses must implement this method."
        raise NotImplementedError(error_message)

    def send_notification_message(self, message: str):
        """Send the notification message."""
        self.queue.enqueue(self.send_message, args=(message,))
