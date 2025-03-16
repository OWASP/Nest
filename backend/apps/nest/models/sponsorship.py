"""Nest app sponsorship model."""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.issue import Issue

DEADLINE_FUTURE_ERROR = "Deadline must be in the future."
ISSUE_LINK_ERROR = "Issue link must belong to an OWASP repository."
PRICE_POSITIVE_ERROR = "Price must be a positive value."


class Sponsorship(BulkSaveModel, TimestampedModel):
    """Sponsorship model."""

    class CurrencyType(models.TextChoices):
        """Currency type choices."""

        EUR = "EUR", "Euro"
        USD = "USD", "US Dollar"

    class Meta:
        db_table = "nest_sponsorships"
        verbose_name_plural = "Sponsorships"

    currency = models.CharField(
        max_length=3, choices=CurrencyType.choices, default=CurrencyType.USD
    )
    deadline_at = models.DateTimeField(null=True, blank=True)
    amount = models.FloatField()
    slack_user_id = models.CharField(max_length=100)

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="sponsorships",
    )

    def __str__(self):
        """Sponsorship human readable representation."""
        return f"Sponsorship for {self.issue.title} by {self.slack_user_id}"

    def clean(self):
        """Validate model data."""
        super().clean()

        # Validate amount is positive
        if self.amount <= 0:
            raise ValidationError(PRICE_POSITIVE_ERROR)

        # Validate deadline is in the future
        if self.deadline_at and self.deadline_at < timezone.now():
            raise ValidationError(DEADLINE_FUTURE_ERROR)

        # Validate GitHub issue link belongs to OWASP
        if not self.issue.url.startswith("https://github.com/OWASP"):
            raise ValidationError(ISSUE_LINK_ERROR)

    def save(self, *args, **kwargs):
        """Override save to run full validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def update_data(sponsorship, **kwargs):
        """Update sponsorship data with the provided fields."""
        fields_to_update = ["amount", "deadline_at", "slack_user_id"]
        for field in fields_to_update:
            if field in kwargs:
                setattr(sponsorship, field, kwargs[field])
        sponsorship.save()
        return sponsorship
