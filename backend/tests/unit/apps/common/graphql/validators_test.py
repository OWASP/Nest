from datetime import UTC, datetime, timedelta

import pytest
from django.core.exceptions import ValidationError

from apps.common.graphql.validators import (
    ensure_aware,
    validate_date_range,
    validate_date_range_within_bounds,
    validate_no_duplicates,
    validate_not_in_past,
)


class TestValidators:
    def test_ensure_aware_makes_naive_datetime_aware(self):
        naive = datetime(2026, 1, 1)  # noqa: DTZ001
        result = ensure_aware(naive)
        assert result.tzinfo is not None

    def test_ensure_aware_leaves_aware_datetime_unchanged(self):
        aware = datetime(2026, 1, 1, tzinfo=UTC)
        result = ensure_aware(aware)
        assert result == aware

    def test_validate_date_range_valid(self):
        started_at = datetime(2026, 1, 1, tzinfo=UTC)
        ended_at = datetime(2026, 2, 1, tzinfo=UTC)
        result_started, result_ended = validate_date_range(started_at, ended_at)
        assert result_started == started_at
        assert result_ended == ended_at

    def test_validate_date_range_raises_when_end_before_start(self):
        started_at = datetime(2026, 2, 1, tzinfo=UTC)
        ended_at = datetime(2026, 1, 1, tzinfo=UTC)
        with pytest.raises(ValidationError, match="End date must be after start date"):
            validate_date_range(started_at, ended_at)

    def test_validate_date_range_raises_when_end_equals_start(self):
        same = datetime(2026, 1, 1, tzinfo=UTC)
        with pytest.raises(ValidationError, match="End date must be after start date"):
            validate_date_range(same, same)

    @pytest.mark.parametrize(
        ("started_at", "ended_at"),
        [
            (None, datetime(2026, 1, 1, tzinfo=UTC)),
            (datetime(2026, 1, 1, tzinfo=UTC), None),
            (None, None),
        ],
    )
    def test_validate_date_range_raises_when_required_and_missing(self, started_at, ended_at):
        with pytest.raises(ValidationError, match="Both start and end dates are required"):
            validate_date_range(started_at, ended_at)

    def test_validate_date_range_allows_missing_when_not_required(self):
        result = validate_date_range(None, None, required=False)
        assert result == (None, None)

    def test_validate_date_range_within_bounds_valid(self):
        validate_date_range_within_bounds(
            datetime(2026, 2, 1, tzinfo=UTC),
            datetime(2026, 3, 1, tzinfo=UTC),
            bounds_started_at=datetime(2026, 1, 1, tzinfo=UTC),
            bounds_ended_at=datetime(2026, 4, 1, tzinfo=UTC),
        )

    def test_validate_date_range_within_bounds_raises_when_starts_too_early(self):
        with pytest.raises(ValidationError, match="start date cannot be before"):
            validate_date_range_within_bounds(
                datetime(2025, 12, 1, tzinfo=UTC),
                datetime(2026, 3, 1, tzinfo=UTC),
                bounds_started_at=datetime(2026, 1, 1, tzinfo=UTC),
                bounds_ended_at=datetime(2026, 4, 1, tzinfo=UTC),
            )

    def test_validate_date_range_within_bounds_raises_when_ends_too_late(self):
        with pytest.raises(ValidationError, match="end date cannot be after"):
            validate_date_range_within_bounds(
                datetime(2026, 2, 1, tzinfo=UTC),
                datetime(2026, 5, 1, tzinfo=UTC),
                bounds_started_at=datetime(2026, 1, 1, tzinfo=UTC),
                bounds_ended_at=datetime(2026, 4, 1, tzinfo=UTC),
            )

    def test_validate_date_range_within_bounds_uses_custom_label(self):
        with pytest.raises(ValidationError, match="before module start date"):
            validate_date_range_within_bounds(
                datetime(2025, 12, 1, tzinfo=UTC),
                datetime(2026, 3, 1, tzinfo=UTC),
                bounds_started_at=datetime(2026, 1, 1, tzinfo=UTC),
                bounds_ended_at=datetime(2026, 4, 1, tzinfo=UTC),
                bounds_label="module",
            )

    def test_validate_no_duplicates_passes_for_unique_values(self):
        validate_no_duplicates(["a", "b", "c"])

    def test_validate_no_duplicates_raises_for_duplicates(self):
        with pytest.raises(ValidationError, match="Duplicate values are not allowed"):
            validate_no_duplicates(["a", "b", "a"])

    def test_validate_no_duplicates_uses_custom_label(self):
        with pytest.raises(ValidationError, match="Duplicate module keys are not allowed"):
            validate_no_duplicates(["x", "x"], field_label="module keys")

    def test_validate_not_in_past_accepts_future_date(self):
        future = datetime.now(tz=UTC) + timedelta(days=1)
        result = validate_not_in_past(future)
        assert result == future

    def test_validate_not_in_past_accepts_today(self):
        today = datetime.now(tz=UTC)
        validate_not_in_past(today)

    def test_validate_not_in_past_raises_for_past_date(self):
        past = datetime.now(tz=UTC) - timedelta(days=1)
        with pytest.raises(ValidationError, match="Date cannot be in the past"):
            validate_not_in_past(past)

    def test_validate_not_in_past_uses_custom_label(self):
        past = datetime.now(tz=UTC) - timedelta(days=1)
        with pytest.raises(ValidationError, match="Deadline cannot be in the past"):
            validate_not_in_past(past, field_label="deadline")
