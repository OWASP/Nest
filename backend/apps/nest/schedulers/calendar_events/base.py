"""Base Scheduler for Nest Calendar Events."""

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
                self.__class__.send_and_delete,
                message=self.reminder_schedule.reminder.message,
                channel_id=self.reminder_schedule.reminder.entity_channel.pk,
                reminder_schedule_id=self.reminder_schedule.pk,
            ).get_id()
        else:
            self.reminder_schedule.job_id = self.scheduler.cron(
                self.reminder_schedule.cron_expression,
                func=self.__class__.send_and_update,
                args=(
                    self.reminder_schedule.reminder.message,
                    self.reminder_schedule.reminder.entity_channel.pk,
                    self.reminder_schedule.pk,
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
    def send_message(message: str, channel_id: int):
        """Send message to the specified channel. To be implemented by subclasses."""
        error_message = "Subclasses must implement this method."
        raise NotImplementedError(error_message)

    @staticmethod
    def send_and_delete(message: str, channel_id: int, reminder_schedule_id: int):
        """Send message to the specified channel and delete the reminder."""
        error_message = "Subclasses must implement this method."
        raise NotImplementedError(error_message)

    @staticmethod
    def send_and_update(message: str, channel_id: int, reminder_schedule_id: int):
        """Send message and update the reminder schedule."""
        error_message = "Subclasses must implement this method."
        raise NotImplementedError(error_message)
