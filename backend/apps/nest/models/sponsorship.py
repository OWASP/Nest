"""Nest app sponsorship model."""

from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.issue import Issue
from apps.nest.constants import (
    DEADLINE_FORMAT_ERROR,
    DEADLINE_FUTURE_ERROR,
    ISSUE_LINK_ERROR,
    PRICE_POSITIVE_ERROR,
    PRICE_VALID_ERROR,
)


class Sponsorship(BulkSaveModel, TimestampedModel):
    """Sponsorship model."""

    class Meta:
        db_table = "nest_sponsorships"
        verbose_name_plural = "Sponsorships"

    deadline_at = models.DateTimeField(null=True, blank=True)
    price_usd = models.FloatField()
    slack_user_id = models.CharField(max_length=100)

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="sponsorships",
    )

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

    @staticmethod
    def validate_deadline(deadline_str):
        """Validate that the deadline is in a valid datetime format."""
        try:
            # Try parsing the deadline in YYYY-MM-DD format
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d").replace(
                tzinfo=timezone.get_current_timezone()
            )
        except ValueError:
            try:
                # Try parsing the deadline in YYYY-MM-DD HH:MM format
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M").replace(
                    tzinfo=timezone.get_current_timezone()
                )
            except ValueError as e:
                raise ValidationError(DEADLINE_FORMAT_ERROR) from e

        if deadline < timezone.now():
            raise ValidationError(DEADLINE_FUTURE_ERROR)

        return deadline

    @staticmethod
    def validate_github_issue_link(issue_link):
        """Validate that the issue link belongs to a valid OWASP-related repository."""
        if not issue_link.startswith("https://github.com/OWASP"):
            raise ValidationError(ISSUE_LINK_ERROR)
        return issue_link

    @staticmethod
    def validate_price(price):
        """Validate that the price is a positive float value."""
        try:
            price = float(price)
            if price <= 0:
                raise ValidationError(PRICE_POSITIVE_ERROR)
        except ValueError as e:
            raise ValidationError(PRICE_VALID_ERROR) from e
        return price
