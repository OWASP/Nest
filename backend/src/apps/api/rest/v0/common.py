"""Common schemas and filters for the API."""

from datetime import UTC, datetime
from typing import Annotated

from django.db.models import F, OuterRef, QuerySet, Subquery
from ninja import Field, FilterLookup, FilterSchema, Schema
from pydantic import AfterValidator

from apps.owasp.models.board_meeting_action import BoardMeetingAction
from apps.owasp.models.entity_member import EntityMember


def normalize_datetime(value: datetime | None) -> datetime | None:
    """Normalize aware datetimes to UTC so PostgreSQL accepts the offset.

    Args:
        value (datetime, optional): The datetime to normalize.

    Returns:
        datetime: The datetime normalized to UTC, or the original value when it is
            ``None`` or timezone-naive.

    Raises:
        ValueError: If the UTC conversion moves the datetime outside the supported
            date range.

    """
    if value is None or value.tzinfo is None:
        return value
    try:
        return value.astimezone(UTC)
    except OverflowError as exc:
        msg = (
            f"Datetime {value.isoformat()} is outside the supported range after UTC normalization"
        )
        raise ValueError(msg) from exc


def annotate_meeting_date(
    queryset: QuerySet, *, action_field: str, outer_ref: str = "pk"
) -> QuerySet:
    """Annotate each row with the date of its parent board meeting.

    Args:
        queryset (QuerySet): The queryset to annotate.
        action_field (str): The ``BoardMeetingAction`` field referencing this model,
            e.g. "discussion", "motion", or "outcome".
        outer_ref (str, optional): The queryset field matching the action foreign key.
            Defaults to "pk".

    Returns:
        QuerySet: The queryset annotated with ``meeting_date``.

    """
    return queryset.annotate(
        meeting_date=Subquery(
            BoardMeetingAction.objects.filter(**{action_field: OuterRef(outer_ref)})
            .order_by("pk")
            .values("meeting__date")[:1]
        )
    )


def order_by_date_field(queryset: QuerySet, ordering: str) -> QuerySet:
    """Order rows by a nullable date field, keeping rows without a date last.

    Args:
        queryset (QuerySet): The queryset to order.
        ordering (str): The date field to order by, prefixed with ``-`` for
            descending order.

    Returns:
        QuerySet: The queryset ordered by the date field and then by descending id.

    """
    date_field = F(ordering.removeprefix("-"))
    order_by = (
        date_field.desc(nulls_last=True)
        if ordering.startswith("-")
        else date_field.asc(nulls_last=True)
    )
    return queryset.order_by(order_by, "-id")


class Leader(Schema):
    """Schema for Leader."""

    key: str | None = None
    name: str


class LocationFilter(FilterSchema):
    """Filter for Location."""

    latitude_gte: float | None = Field(
        None, description="Latitude greater than or equal to", q="latitude__gte"
    )
    latitude_lte: float | None = Field(
        None, description="Latitude less than or equal to", q="latitude__lte"
    )
    longitude_gte: float | None = Field(
        None, description="Longitude greater than or equal to", q="longitude__gte"
    )
    longitude_lte: float | None = Field(
        None, description="Longitude less than or equal to", q="longitude__lte"
    )


class MeetingDateFilter(FilterSchema):
    """Filter for board activity by parent meeting date."""

    date_gte: Annotated[
        datetime | None,
        FilterLookup(q="meeting_date__gte"),
        AfterValidator(normalize_datetime),
    ] = Field(
        None,
        description="Parent meeting date greater than or equal to (ISO 8601)",
    )
    date_lte: Annotated[
        datetime | None,
        FilterLookup(q="meeting_date__lte"),
        AfterValidator(normalize_datetime),
    ] = Field(
        None,
        description="Parent meeting date less than or equal to (ISO 8601)",
    )


class Person(Schema):
    """Reference to a person represented by an EntityMember row."""

    id: int
    name: str

    @staticmethod
    def resolve_name(obj: EntityMember) -> str:
        """Resolve the display name for the referenced person."""
        return obj.member.login if obj.member_id else obj.member_name


class ValidationErrorSchema(Schema):
    """Schema for validation error."""

    message: str
    errors: list[dict] | dict | None = None
