"""OWASP app event model."""

from dateutil import parser
from django.db import models
from django.utils import timezone

from apps.common.constants import NL
from apps.common.geocoding import get_location_coordinates
from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.open_ai import OpenAi
from apps.common.utils import join_values, slugify
from apps.github.utils import normalize_url


class Event(BulkSaveModel, TimestampedModel):
    """Event model."""

    class Meta:
        db_table = "owasp_events"
        verbose_name_plural = "Events"

    class Category(models.TextChoices):
        """Event category."""

        APPSEC_DAYS = "appsec_days", "AppSec Days"
        GLOBAL = "global", "Global"
        OTHER = "other", "Other"
        PARTNER = "partner", "Partner"

    category = models.CharField(
        verbose_name="Category",
        max_length=11,
        choices=Category.choices,
        default=Category.OTHER,
    )
    name = models.CharField(verbose_name="Name", max_length=100)
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date", null=True, blank=True)
    description = models.TextField(verbose_name="Description", default="", blank=True)
    key = models.CharField(verbose_name="Key", max_length=100, unique=True)
    summary = models.TextField(verbose_name="Summary", blank=True, default="")
    suggested_location = models.CharField(
        verbose_name="Suggested Location", max_length=255, blank=True, default=""
    )
    url = models.URLField(verbose_name="URL", default="", blank=True)
    latitude = models.FloatField(verbose_name="Latitude", null=True, blank=True)
    longitude = models.FloatField(verbose_name="Longitude", null=True, blank=True)

    def __str__(self):
        """Event human readable representation."""
        return f"{self.name or self.key}"

    @staticmethod
    def upcoming_events():
        """Get upcoming events."""
        return Event.objects.filter(
            start_date__gt=timezone.now(),
        ).order_by(
            "start_date",
        )

    @staticmethod
    def bulk_save(events, fields=None):
        """Bulk save events."""
        BulkSaveModel.bulk_save(Event, events, fields=fields)

    # TODO(arkid15r): refactor this when there is a chance.
    @staticmethod
    def parse_dates(dates, start_date):
        """Parse event dates."""
        if not dates:
            return None

        # Handle single-day events (e.g., "March 14, 2025")
        if "," in dates and "-" not in dates:
            try:
                return parser.parse(dates).date()
            except ValueError:
                return None

        # Handle date ranges (e.g., "May 26-30, 2025" or "November 2-6, 2026")
        if "-" in dates and "," in dates:
            try:
                # Split the date range into parts
                date_range, year = dates.split(", ")
                month_day_range = date_range.split()

                # Extract month and day range
                month = month_day_range[0]
                day_range = month_day_range[1]

                # Extract end day from the range
                end_day = int(day_range.split("-")[-1])

                # Parse the year
                year = int(year.strip())

                # Use the start_date to determine the month if provided
                if start_date:
                    start_date_parsed = start_date
                    month = start_date_parsed.strftime("%B")  # Full month name (e.g., "May")

                # Parse the full end date string
                end_date_str = f"{month} {end_day}, {year}"
                return parser.parse(end_date_str).date()
            except (ValueError, IndexError, AttributeError):
                return None

        return None

    @staticmethod
    def update_data(category, data, save=True):
        """Update event data."""
        key = slugify(data["name"])
        try:
            event = Event.objects.get(key=key)
        except Event.DoesNotExist:
            event = Event(key=key)

        event.from_dict(category, data)
        if save:
            event.save()

        return event

    def from_dict(self, category, data):
        """Update instance based on the dict data."""
        fields = {
            "category": {
                "AppSec Days": Event.Category.APPSEC_DAYS,
                "Global": Event.Category.GLOBAL,
                "Partner": Event.Category.PARTNER,
            }.get(category, Event.Category.OTHER),
            "description": data.get("optional-text", ""),
            "end_date": Event.parse_dates(data.get("dates", ""), data.get("start-date")),
            "name": data["name"],
            "start_date": parser.parse(data["start-date"]).date()
            if isinstance(data["start-date"], str)
            else data["start-date"],
            "url": normalize_url(data.get("url", "")) or "",
        }

        for key, value in fields.items():
            setattr(self, key, value)

    def generate_geo_location(self):
        """Add latitude and longitude data."""
        location = None
        if self.suggested_location and self.suggested_location != "None":
            location = get_location_coordinates(self.suggested_location)
        if location is None:
            location = get_location_coordinates(self.get_context())
        if location:
            self.latitude = location.latitude
            self.longitude = location.longitude

    def generate_suggested_location(self, prompt):
        """Generate a suggested location for the event."""
        open_ai = OpenAi()
        open_ai.set_input(self.get_context())
        open_ai.set_max_tokens(100).set_prompt(prompt)
        try:
            suggested_location = open_ai.complete()
            self.suggested_location = (
                suggested_location if suggested_location and suggested_location != "None" else ""
            )
        except (ValueError, TypeError):
            self.suggested_location = ""

    def generate_summary(self, prompt):
        """Generate a summary for the event."""
        open_ai = OpenAi()
        open_ai.set_input(self.get_context(include_dates=True))
        open_ai.set_max_tokens(100).set_prompt(prompt)
        try:
            summary = open_ai.complete()
            self.summary = summary if summary and summary != "None" else ""
        except (ValueError, TypeError):
            self.summary = ""

    def get_context(self, include_dates=False):
        """Return geo string."""
        context = [
            f"Name: {self.name}",
            f"Description: {self.description}",
            f"Summary: {self.summary}",
        ]
        if include_dates:
            context.append(f"Dates: {self.start_date} - {self.end_date}")

        return join_values(
            context,
            delimiter=NL,
        )
