from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from django.db.models import F

from apps.api.rest.v0.common import (
    LocationFilter,
    MeetingDateFilter,
    Person,
    annotate_meeting_date,
    normalize_datetime,
    order_by_date_field,
)
from apps.owasp.models.board_motion import BoardMotion
from apps.owasp.models.board_vote import BoardVote


class TestNormalizeDatetime:
    """Tests for the normalize_datetime helper."""

    def test_none_is_returned_unchanged(self):
        """None passes through untouched."""
        assert normalize_datetime(None) is None

    def test_naive_datetime_is_returned_unchanged(self):
        """Naive datetimes have no offset to normalize."""
        value = datetime(2024, 1, 1, 12, 0, 0)  # noqa: DTZ001

        assert normalize_datetime(value) is value

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("1447-05-09T03:57:07.246491-22:14", "1447-05-10T02:11:07.246491+00:00"),
            ("8292-12-23T16:24:08.050762+21:14", "8292-12-22T19:10:08.050762+00:00"),
        ],
    )
    def test_out_of_range_offsets_are_converted_to_utc(self, raw, expected):
        """Offsets PostgreSQL rejects are normalized while preserving the instant."""
        assert normalize_datetime(datetime.fromisoformat(raw)) == datetime.fromisoformat(expected)

    def test_in_range_offset_is_converted_to_utc(self):
        """Valid offsets are also normalized to UTC."""
        value = datetime(
            2024,
            1,
            1,
            12,
            0,
            0,
            tzinfo=timezone(timedelta(hours=5, minutes=30)),
        )

        assert normalize_datetime(value) == datetime(2024, 1, 1, 6, 30, tzinfo=UTC)

    def test_utc_conversion_overflow_raises_value_error(self):
        """Boundary datetimes that overflow the supported range are rejected."""
        value = datetime(1, 1, 1, tzinfo=timezone(timedelta(hours=14)))

        with pytest.raises(ValueError, match="outside the supported range"):
            normalize_datetime(value)


class TestAnnotateMeetingDate:
    """Tests for the annotate_meeting_date correlation."""

    def test_correlates_on_primary_key_by_default(self):
        """The default outer_ref matches the target row primary key."""
        query = str(annotate_meeting_date(BoardMotion.objects.all(), action_field="motion").query)

        assert '"owasp_board_meeting_actions"' in query
        assert '"motion_id" = ("owasp_board_motions"."id")' in query

    def test_correlates_on_custom_outer_ref(self):
        """A custom outer_ref matches the given field instead of the primary key."""
        query = str(
            annotate_meeting_date(
                BoardVote.objects.all(),
                action_field="motion",
                outer_ref="motion_id",
            ).query
        )

        assert '"motion_id" = ("owasp_board_votes"."motion_id")' in query


class TestOrderByDateField:
    """Tests for the order_by_date_field helper."""

    def test_ascending_orders_nulls_last(self):
        """Ascending order keeps rows without a date last."""
        queryset = MagicMock()

        result = order_by_date_field(queryset, "meeting_date")

        queryset.order_by.assert_called_once_with(F("meeting_date").asc(nulls_last=True), "-id")
        assert result == queryset.order_by.return_value

    def test_descending_orders_nulls_last(self):
        """Descending order keeps rows without a date last."""
        queryset = MagicMock()

        result = order_by_date_field(queryset, "-due_date")

        queryset.order_by.assert_called_once_with(F("due_date").desc(nulls_last=True), "-id")
        assert result == queryset.order_by.return_value


class TestLocationFilter:
    @pytest.mark.parametrize(
        "location_data",
        [
            {
                "latitude_gte": -5.0,
                "latitude_lte": 5.0,
                "longitude_gte": -10.0,
                "longitude_lte": 10.0,
            },
            {
                "latitude_gte": 15.0,
                "latitude_lte": 25.0,
                "longitude_gte": 20.0,
                "longitude_lte": 30.0,
            },
        ],
    )
    def test_location_filter_validation(self, location_data):
        location_filter = LocationFilter(**location_data)

        assert location_filter.latitude_gte == location_data["latitude_gte"]
        assert location_filter.latitude_lte == location_data["latitude_lte"]
        assert location_filter.longitude_gte == location_data["longitude_gte"]
        assert location_filter.longitude_lte == location_data["longitude_lte"]


class TestMeetingDateFilter:
    """Tests for the shared meeting date filter."""

    def test_date_filters_map_to_meeting_date_lookups(self):
        """Date filters target the annotated meeting date and normalize offsets."""
        filters = MeetingDateFilter(
            date_gte="1447-05-09T03:57:07.246491-22:14",
            date_lte="8292-12-23T16:24:08.050762+21:14",
        )

        children = dict(filters.get_filter_expression().children)

        assert children["meeting_date__gte"] == datetime(1447, 5, 10, 2, 11, 7, 246491, tzinfo=UTC)
        assert children["meeting_date__lte"] == datetime(
            8292, 12, 22, 19, 10, 8, 50762, tzinfo=UTC
        )


class TestPerson:
    """Tests for the Person schema."""

    def test_resolve_name_uses_login_when_matched(self):
        """Prefer the matched User login when member_id is set."""
        entity = MagicMock()
        entity.id = 1
        entity.member_id = 42
        entity.member.login = "john_doe"
        entity.member_name = "John Doe"

        ref = Person.from_orm(entity)

        assert ref.id == 1
        assert ref.name == "john_doe"

    def test_resolve_name_falls_back_to_member_name(self):
        """Fall back to member_name when no matched User exists."""
        entity = MagicMock()
        entity.id = 2
        entity.member_id = None
        entity.member_name = "Jane Director"

        ref = Person.from_orm(entity)

        assert ref.id == 2
        assert ref.name == "Jane Director"
