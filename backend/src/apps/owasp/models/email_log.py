"""OWASP app email log model."""

from django.db import models

from apps.owasp.models.snapshot import Snapshot
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


class EmailLog(models.Model):
    """Model for tracking sent digest emails and preventing duplicates.

    Each log entry links a SnapshotSubscription to the Snapshot it was sent for.
    The unique constraint ensures no duplicate emails per subscription per snapshot.
    """

    class Meta:
        """Model options."""

        db_table = "owasp_email_logs"
        verbose_name_plural = "Email Logs"
        constraints = [
            models.UniqueConstraint(
                fields=["snapshot_subscription", "snapshot"],
                condition=models.Q(status="sent"),
                name="unique_email_per_subscription_snapshot",
            ),
        ]
        indexes = [
            models.Index(fields=["-created_at"], name="owasp_email_log_created_idx"),
        ]

    class Status(models.TextChoices):
        """Email delivery status choices."""

        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    snapshot_subscription = models.ForeignKey(
        SnapshotSubscription,
        on_delete=models.CASCADE,
        related_name="email_logs",
    )
    snapshot = models.ForeignKey(
        Snapshot,
        on_delete=models.CASCADE,
        related_name="email_logs",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
    )
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation."""
        return f"{self.snapshot_subscription.user} — {self.snapshot.key} ({self.status})"

    @classmethod
    def is_duplicate(cls, *, snapshot, snapshot_subscription):
        """Check if a digest email has already been sent.

        Args:
            snapshot: The snapshot instance.
            snapshot_subscription: The snapshot subscription instance.

        Returns:
            True if a log entry already exists for this combination.

        """
        return cls.objects.filter(
            snapshot=snapshot,
            snapshot_subscription=snapshot_subscription,
            status=cls.Status.SENT,
        ).exists()

    @classmethod
    def mark_sent(cls, *, snapshot, snapshot_subscription):
        """Record a successfully sent email.

        Args:
            snapshot: The snapshot instance.
            snapshot_subscription: The snapshot subscription instance.

        Returns:
            The created EmailLog instance.

        """
        return cls.objects.create(
            snapshot=snapshot,
            snapshot_subscription=snapshot_subscription,
            status=cls.Status.SENT,
        )

    @classmethod
    def mark_failed(cls, *, snapshot, snapshot_subscription, error_message=""):
        """Record a failed email delivery attempt.

        Args:
            snapshot: The snapshot instance.
            snapshot_subscription: The snapshot subscription instance.
            error_message: Description of the failure.

        Returns:
            The created EmailLog instance.

        """
        return cls.objects.create(
            snapshot=snapshot,
            snapshot_subscription=snapshot_subscription,
            status=cls.Status.FAILED,
            error_message=error_message,
        )
