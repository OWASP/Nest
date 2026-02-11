"""OWASP app event model."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from apps.core.models.prompt import Prompt

if TYPE_CHECKING:  # pragma: no cover
    from datetime import date

from datetime import datetime

from dateutil import parser
from django.db import models
from django.db.models import Q
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
        """Model options."""

        db_table = "owasp_events"
        indexes = [
            models.Index(fields=["-start_date"], name="event_start_date_desc_idx"),
            models.Index(fields=["-end_date"], name="event_end_date_desc_idx"),
        ]
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

    def __str__(self) -> str:
        """Event human readable representation."""
        return f"{self.name or self.key}"

    @staticmethod
    def upcoming_events():
        """Get upcoming events.

        Returns:
            QuerySet: A queryset of upcoming Event instances ordered by start date.

        """
        return (
            Event.objects.filter(
                start_date__gt=timezone.now(),
            )
            .exclude(
                Q(name__exact="") | Q(url__exact=""),
            )
            .order_by(
                "start_date",
            )
        )

    @staticmethod
    def bulk_save(  # type: ignore[override]
        events: list,
        fields: tuple[str, ...] | None = None,
    ) -> None:
        """Bulk save events.

        Args:
            events (list): A list of Event instances to be saved.
            fields (list, optional): A list of fields to update during the bulk save.

        Returns:
            None

        """
        BulkSaveModel.bulk_save(Event, events, fields=fields)

    # TODO(arkid15r): refactor this when there is a chance.
    @staticmethod
    def parse_dates(dates: str, start_date: date) -> date | None:  # noqa: PLR0911
        """Parse event dates.

        Args:
            dates (str): A string representing the event dates.
            start_date (datetime.date): The start date of the event.

        Returns:
            datetime.date or None: The parsed end date if successful, otherwise None.

        """
        if not dates:
            return None

        max_day_length = 2

        # Normalize dashes (hyphen, en-dash, em-dash).
        clean_dates = re.sub(r"[\-\–\—]", "-", dates)  # noqa: RUF001

        # Guard against ISO-like single dates (e.g. "2025-05-26").
        if re.match(r"^\d{4}-\d{2}-\d{2}$", clean_dates.strip()):
            try:
                return parser.parse(clean_dates.strip()).date()
            except (TypeError, ValueError):
                return None

        try:
            if "-" in clean_dates:
                parts = clean_dates.split("-")
                end_str = parts[-1].strip()

                day_match = re.match(r"^(\d{1,2})", end_str)
                if day_match:
                    day_value = day_match.group(1)
                    if len(end_str) <= max_day_length or "," in end_str:
                        return start_date.replace(day=int(day_value))

                end_date = parser.parse(
                    end_str, default=datetime.combine(start_date, datetime.min.time())
                ).date()
                # Handle year crossover: if end_date is before start_date, assume next year.
                if end_date < start_date:
                    end_date = end_date.replace(year=end_date.year + 1)
                return end_date

            return parser.parse(clean_dates.strip()).date()

        except (IndexError, OverflowError, TypeError, ValueError):
            return None

    @staticmethod
    def update_data(category, data, *, save: bool = True) -> Event | None:
        """Update event data.

        Args:
            category (str): The category of the event.
            data (dict): A dictionary containing event data.
            save (bool, optional): Whether to save the event instance.

        Returns:
            Event: The updated or newly created Event instance.

        """
        key = slugify(data["name"])
        try:
            event = Event.objects.get(key=key)
        except Event.DoesNotExist:
            event = Event(key=key)

        try:
            event.from_dict(category, data)
        except KeyError:
            return None

        if save:
            event.save()

        return event

    def from_dict(self, category: str, data: dict) -> None:
        """Update instance based on the dict data.

        Args:
            category (str): The category of the event.
            data (dict): A dictionary containing event data.

        Returns:
            None

        """
        start_date = data["start-date"]
        fields = {
            "category": {
                "AppSec Days": Event.Category.APPSEC_DAYS,
                "Global": Event.Category.GLOBAL,
                "Partner": Event.Category.PARTNER,
            }.get(category, Event.Category.OTHER),
            "description": data.get("optional-text", ""),
            "end_date": Event.parse_dates(data.get("dates", ""), start_date),
            "name": data["name"],
            "start_date": parser.parse(start_date).date()
            if isinstance(start_date, str)
            else start_date,
            "url": normalize_url(data.get("url", "")) or "",
        }

        for key, value in fields.items():
            setattr(self, key, value)

    def generate_geo_location(self) -> None:
        """Add latitude and longitude data.

        Returns:
            None

        """
        location = None
        if self.suggested_location and self.suggested_location != "None":
            location = get_location_coordinates(self.suggested_location)
        if location is None:
            location = get_location_coordinates(self.get_context())
        if location:
            self.latitude = location.latitude
            self.longitude = location.longitude

    def generate_suggested_location(self, prompt=None) -> None:
        """Generate a suggested location for the event.

        Args:
            prompt (str): The prompt to be used for generating the suggested location.

        Returns:
            None

        """
        open_ai = OpenAi()
        open_ai.set_input(self.get_context())
        open_ai.set_max_tokens(100).set_prompt(
            prompt or Prompt.get_owasp_event_suggested_location()
        )
        try:
            suggested_location = open_ai.complete()
            self.suggested_location = (
                suggested_location if suggested_location and suggested_location != "None" else ""
            )
        except (ValueError, TypeError):
            self.suggested_location = ""

    def generate_summary(self, prompt=None) -> None:
        """Generate a summary for the event.

        Args:
            prompt (str): The prompt to be used for generating the summary.

        Returns:
            None

        """
        open_ai = OpenAi()
        open_ai.set_input(self.get_context(include_dates=True))
        open_ai.set_max_tokens(100).set_prompt(prompt or Prompt.get_owasp_event_summary())
        try:
            summary = open_ai.complete()
            self.summary = summary if summary and summary != "None" else ""
        except (ValueError, TypeError):
            self.summary = ""

    def get_context(self, *, include_dates: bool = False) -> str:
        """Return geo string.

        Args:
            include_dates (bool, optional): Whether to include event dates in the context.

        Returns:
            str: The generated context string.

        """
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

    def save(self, *args, **kwargs):
        """Save the event instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        if not self.suggested_location:
            self.generate_suggested_location()

        if self.latitude is None or self.longitude is None:
            self.generate_geo_location()

        super().save(*args, **kwargs)
