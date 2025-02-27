"""Nest app sponsorship model."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.issue import Issue


class Sponsorship(BulkSaveModel, TimestampedModel):
    """Sponsorship model."""

    deadline_at = models.DateTimeField(null=True, blank=True)
    price_usd = models.FloatField()
    slack_user_id = models.CharField(max_length=100)

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="sponsorships",
    )

    class Meta:
        db_table = "nest_sponsorships"
        verbose_name_plural = "Sponsorships"

    def __str__(self):
        """Sponsorship human readable representation."""
        return f"Sponsorship for {self.issue.title} by {self.slack_user_id}"

    @staticmethod
    def update_data(sponsorship, **kwargs):
        """Update sponsorship data with the provided fields."""
        fields_to_update = ["price_usd", "deadline_at", "slack_user_id"]
        for field in fields_to_update:
            if field in kwargs:
                setattr(sponsorship, field, kwargs[field])
        sponsorship.save()
        return sponsorship
