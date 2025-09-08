"""Nest Reminder Schedule model."""

from django.db import models


class ReminderSchedule(models.Model):
    """Model representing a reminder schedule."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reminder", "scheduled_time"],
                name="unique_reminder_schedule",
            )
        ]
        db_table = "nest_reminder_schedules"
        verbose_name = "Nest Reminder Schedule"
        verbose_name_plural = "Nest Reminder Schedules"

    class Recurrence(models.TextChoices):
        ONCE = "once", "Once"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    reminder = models.ForeignKey(
        "nest.Reminder",
        verbose_name="Nest Reminder",
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    scheduled_time = models.DateTimeField(verbose_name="Scheduled Time")
    recurrence = models.CharField(
        verbose_name="Recurrence",
        max_length=50,
        choices=Recurrence.choices,
        default=Recurrence.ONCE,
    )

    @property
    def cron_expression(self) -> str | None:
        """Get cron expression for the scheduled time."""
        time_str = f"{self.scheduled_time.minute} {self.scheduled_time.hour}"
        match self.recurrence:
            case self.Recurrence.DAILY:
                return f"{time_str} * * *"
            case self.Recurrence.WEEKLY:
                return f"{time_str} * * {self.scheduled_time.weekday()}"
            case self.Recurrence.MONTHLY:
                return f"{time_str} {self.scheduled_time.day} * *"
            # For 'once' or any other case, return None
            case _:
                return None

    def __str__(self) -> str:
        """Reminder Schedule human readable representation."""
        return f"Schedule for {self.reminder} at {self.scheduled_time} ({self.recurrence})"
