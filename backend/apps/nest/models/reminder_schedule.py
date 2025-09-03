"""Nest Reminder Schedule model."""

from django.db import models


class ReminderSchedule(models.Model):
    """Model representing a reminder schedule."""

    class Meta:
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

    def __str__(self) -> str:
        """Reminder Schedule human readable representation."""
        return f"Schedule for {self.reminder} at {self.scheduled_time} ({self.recurrence})"
