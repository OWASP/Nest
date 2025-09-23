"""Base Scheduler for Nest Calendar Events."""

from django.utils import timezone
from django_rq import get_scheduler

from apps.nest.models.reminder_schedule import ReminderSchedule


class BaseScheduler:
    """Base Scheduler Class for Nest Calendar Events."""

    def __init__(self, reminder_schedule: ReminderSchedule):
        """Initialize the BaseScheduler with a ReminderSchedule instance."""
        self.reminder_schedule = reminder_schedule
        self.scheduler = get_scheduler("default")

    def schedule(self):
        """Schedule the reminder."""
        if self.reminder_schedule.recurrence == ReminderSchedule.Recurrence.ONCE:
            self.reminder_schedule.job_id = self.scheduler.enqueue_at(
                self.reminder_schedule.scheduled_time,
                self.__class__.send_message,
                message=self.reminder_schedule.reminder.message,
                channel_id=self.reminder_schedule.reminder.channel_id,
            ).get_id()

            # Schedule deletion of the reminder after sending the message
            self.scheduler.enqueue_at(
                self.reminder_schedule.scheduled_time + timezone.timedelta(minutes=1),
                self.reminder_schedule.reminder.delete,
            )
        else:
            self.reminder_schedule.job_id = self.scheduler.cron(
                self.reminder_schedule.cron_expression,
                func=self.__class__.send_message_and_update,
                args=(
                    self.reminder_schedule.reminder.message,
                    self.reminder_schedule.reminder.channel_id,
                    self.reminder_schedule,
                ),
                queue_name="default",
                use_local_timezone=True,
                result_ttl=500,
            ).get_id()

        self.reminder_schedule.save(update_fields=["job_id"])

    def cancel(self):
        """Cancel the scheduled reminder."""
        if self.reminder_schedule.job_id:
            self.scheduler.cancel(self.reminder_schedule.job_id)
            self.reminder_schedule.reminder.delete()

    @staticmethod
    def send_message(message: str, channel_id: str):
        """Send message to the specified channel. To be implemented by subclasses."""
        error_message = "Subclasses must implement this method."
        raise NotImplementedError(error_message)

    @staticmethod
    def send_message_and_update(
        message: str, channel_id: str, reminder_schedule: ReminderSchedule
    ):
        """Send message and update the reminder schedule."""
        error_message = "Subclasses must implement this method."
        raise NotImplementedError(error_message)
