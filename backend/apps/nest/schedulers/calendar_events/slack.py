"""Slack Scheduler for Nest Calendar Events."""

from apps.nest.models.reminder_schedule import ReminderSchedule
from apps.nest.schedulers.calendar_events.base import BaseScheduler
from apps.nest.schedulers.tasks.slack import send_message


class SlackScheduler(BaseScheduler):
    """Slack Scheduler Class for Nest Calendar Events."""

    def schedule(self):
        """Schedule the reminder."""
        if self.reminder_schedule.recurrence == ReminderSchedule.Recurrence.ONCE:
            self.scheduler.enqueue_at(
                self.reminder_schedule.scheduled_time,
                send_message,
                message=self.reminder_schedule.reminder.message,
                channel_id=self.reminder_schedule.reminder.channel_id,
            )
            return

        self.scheduler.cron(
            self.reminder_schedule.cron_expression,
            func=send_message,
            args=(
                self.reminder_schedule.reminder.message,
                self.reminder_schedule.reminder.channel_id,
            ),
            queue_name="default",
            use_local_timezone=True,
        )
