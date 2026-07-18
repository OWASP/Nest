"""Github app activity event model."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.enums.activity_event import ActivityType


class ActivityEvent(BulkSaveModel, TimestampedModel):
    """Represents a discrete GitHub activity event linked to a single source object.

    Uses a polymorphic GenericForeignKey to reference the source object.
    """

    class Meta:
        """Model options."""

        db_table = "github_activity_events"
        verbose_name_plural = "Activity Events"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "activity_type",
                    "content_type",
                    "object_id",
                    "occurred_at",
                ],
                name="unique_activity_event",
            ),
        ]

        indexes = [
            models.Index(fields=["activity_type"], name="activity_event_type_idx"),
            models.Index(fields=["actor"], name="activity_event_actor_idx"),
            models.Index(
                fields=["content_type", "object_id"],
                name="activity_event_source_idx",
            ),
            models.Index(fields=["occurred_at"], name="activity_event_occurred_at_idx"),
            models.Index(fields=["repository"], name="activity_event_repository_idx"),
        ]

    activity_type = models.CharField(
        verbose_name="Activity Type",
        max_length=32,
        choices=ActivityType.choices,
    )
    actor = models.ForeignKey(
        "github.User",
        verbose_name="Actor",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="activity_events",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    occurred_at = models.DateTimeField(
        verbose_name="Occurred at",
        help_text="Timestamp when the activity event occurred on GitHub",
    )
    repository = models.ForeignKey(
        "github.Repository",
        verbose_name="Repository",
        on_delete=models.CASCADE,
        related_name="activity_events",
    )
    source_object = GenericForeignKey("content_type", "object_id")

    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"{self.activity_type} by {self.actor} in {self.repository}"

    @staticmethod
    def bulk_save(activity_events, fields=None) -> None:  # type: ignore[override]
        """Bulk save activity events."""
        BulkSaveModel.bulk_save(ActivityEvent, activity_events, fields=fields)
