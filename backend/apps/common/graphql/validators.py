"""Shared input validators for GraphQL mutations.

These validators centralize checks that recur across mutations (date ranges,
duplicate keys, required-together fields) so resolvers don't reimplement
the same logic with slightly different error messages or calling conventions.

All validators raise django.core.exceptions.ValidationError on failure,
matching the existing convention in apps/mentorship/api/internal/mutations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.utils import timezone

if TYPE_CHECKING:
    from datetime import datetime


def ensure_aware(value: datetime) -> datetime:
    """Return a timezone-aware version of a datetime, making it aware if needed."""
    return timezone.make_aware(value) if timezone.is_naive(value) else value


def validate_date_range(
    started_at: datetime | None,
    ended_at: datetime | None,
    *,
    required: bool = True,
) -> tuple[datetime, datetime] | tuple[None, None]:
    """Validate that ended_at is after started_at, normalizing both to aware datetimes.

    Args:
        started_at: Start of the range.
        ended_at: End of the range.
        required: If True, raises when either value is missing.

    Returns:
        A tuple of (started_at, ended_at) normalized to timezone-aware datetimes,
        or (None, None) if both are missing and required=False.

    Raises:
        ValidationError: If required fields are missing or ended_at <= started_at.

    """
    if started_at is None or ended_at is None:
        if required:
            msg = "Both start and end dates are required."
            raise ValidationError(msg)
        return None, None

    started_at = ensure_aware(started_at)
    ended_at = ensure_aware(ended_at)

    if ended_at <= started_at:
        msg = "End date must be after start date."
        raise ValidationError(msg)

    return started_at, ended_at


def validate_date_range_within_bounds(
    started_at: datetime,
    ended_at: datetime,
    *,
    bounds_started_at: datetime,
    bounds_ended_at: datetime,
    subject_label: str = "",
    bounds_label: str = "the parent",
) -> None:
    """Validate that a date range falls fully within an enclosing range.

    Args:
        started_at: Start of the inner range (already validated/aware).
        ended_at: End of the inner range (already validated/aware).
        bounds_started_at: Start of the enclosing range.
        bounds_ended_at: End of the enclosing range.
        subject_label: Human-readable name for the inner range's subject,
            used as the leading word in error messages (e.g. "Module").
        bounds_label: Human-readable name for the enclosing range, used in
            error messages (e.g. "program").

    Raises:
        ValidationError: If the inner range escapes the enclosing range.

    """
    prefix = f"{subject_label} " if subject_label else ""

    if started_at < bounds_started_at:
        msg = f"{prefix}start date cannot be before {bounds_label} start date."
        raise ValidationError(msg)

    if ended_at > bounds_ended_at:
        msg = f"{prefix}end date cannot be after {bounds_label} end date."
        raise ValidationError(msg)


def validate_no_duplicates(values: list[str], *, field_label: str = "values") -> None:
    """Validate that a list contains no duplicate entries.

    Args:
        values: The list to check.
        field_label: Human-readable name for the field, used in error messages.

    Raises:
        ValidationError: If duplicates are found.

    """
    if len(set(values)) != len(values):
        msg = f"Duplicate {field_label} are not allowed."
        raise ValidationError(msg)


def validate_not_in_past(value: datetime, *, field_label: str = "date") -> datetime:
    """Validate that a datetime is not in the past, normalizing to aware.

    Args:
        value: The datetime to check.
        field_label: Human-readable name for the field, used in error messages.

    Returns:
        The normalized, timezone-aware datetime.

    Raises:
        ValidationError: If the date is in the past.

    """
    value = ensure_aware(value)
    if value.date() < timezone.now().date():
        msg = f"{field_label.capitalize()} cannot be in the past."
        raise ValidationError(msg)
    return value
