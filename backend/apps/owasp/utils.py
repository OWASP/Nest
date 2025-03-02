"""OWASP utils."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

from dateutil import parser


def parse_event_dates(dates: str, start_date: str | None = None) -> date | None:
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
