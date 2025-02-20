"""OWASP app event model."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel


class EventCategory(models.TextChoices):
    """Event category choices."""

    GLOBAL = "global", "Global"
    APPSEC_DAYS = "appsec_days", "AppSec Days"
    PARTNER = "partner", "Partner"
    OTHER = "other", "Other"


class Event(BulkSaveModel, TimestampedModel):
    """Event model."""

    class Meta:
        db_table = "owasp_events"
        verbose_name_plural = "Events"

    category = models.CharField(
        verbose_name="Category",
        max_length=20,
        choices=EventCategory.choices,
        default=EventCategory.OTHER,
    )

    category_description = models.TextField(
        verbose_name="Category Description", default="", blank=True
    )
    end_date = models.DateField(verbose_name="End Date", null=True, blank=True)
    key = models.CharField(verbose_name="Key", max_length=100, unique=True)
    name = models.CharField(verbose_name="Name", max_length=100)
    description = models.TextField(verbose_name="Description", default="", blank=True)
    start_date = models.DateField(verbose_name="Start Date", default="2025-01-01", blank=True)
    url = models.URLField(verbose_name="URL", default="", blank=True)

    def __str__(self):
        """Event human readable representation."""
        return f"{self.name or self.key}"

    @staticmethod
    def bulk_save(events, fields=None):
        """Bulk save events."""
        BulkSaveModel.bulk_save(Event, events, fields=fields)
