"""Nest Reminder model."""

from django.db import models
from django.utils import timezone

from apps.nest.models.reminder_schedule import ReminderSchedule
from apps.slack.models.member import Member


class Reminder(models.Model):
    """Model representing a reminder."""

    class Meta:
        db_table = "nest_reminders"
        verbose_name = "Nest Reminder"
        verbose_name_plural = "Nest Reminders"

    channel_id = models.CharField(verbose_name="Channel ID", max_length=15, default="")
    event = models.ForeignKey(
        "owasp.Event",
        verbose_name="Event",
        on_delete=models.SET_NULL,
        related_name="reminders",
        null=True,
    )
    member = models.ForeignKey(
        "slack.Member",
        verbose_name="Slack Member",
        on_delete=models.SET_NULL,
        related_name="reminders",
        null=True,
    )
    message = models.TextField(verbose_name="Reminder Message")

    @staticmethod
    def set_reminder(
        channel: str,
        event,
        slack_user_id: str,
        reminder_time: timezone.datetime,
        recurrence: str,
        message: str = "",
    ):
        """Set a reminder for a user."""
        member = Member.objects.get(slack_user_id=slack_user_id)
        reminder = Reminder.objects.create(
            channel_id=channel,
            event=event,
            member=member,
            message=message,
        )
        ReminderSchedule.objects.create(
            reminder=reminder,
            scheduled_time=reminder_time,
            recurrence=recurrence,
        )

    def __str__(self) -> str:
        """Reminder human readable representation."""
        return f"Reminder for {self.member} in channel: {self.channel_id}: {self.message}"
